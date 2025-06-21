from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
from enum import Enum


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class OrderStatus(str, Enum):
    OPEN = "open"
    CLAIMED = "claimed"
    IN_PROGRESS = "in_progress" 
    SUBMITTED = "submitted"
    COMPLETED = "completed"
    REJECTED = "rejected"

class OrderCategory(str, Enum):
    WEB_SCRAPING = "web_scraping"
    DATA_PROCESSING = "data_processing"
    API_INTEGRATION = "api_integration"
    WORKFLOW_AUTOMATION = "workflow_automation"
    EMAIL_AUTOMATION = "email_automation"
    FILE_PROCESSING = "file_processing"
    DATABASE_AUTOMATION = "database_automation"
    OTHER = "other"

# Models
class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    category: OrderCategory
    payment_amount: float
    requirements: List[str]
    created_by: str  # User email/name
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: OrderStatus = OrderStatus.OPEN
    claimed_by: Optional[str] = None
    claimed_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    delivery_url: Optional[str] = None
    delivery_description: Optional[str] = None
    average_rating: float = 0.0
    rating_count: int = 0
    total_rating_score: int = 0

class OrderCreate(BaseModel):
    title: str
    description: str
    category: OrderCategory
    payment_amount: float
    requirements: List[str]
    created_by: str

class OrderClaim(BaseModel):
    claimed_by: str

class OrderSubmission(BaseModel):
    delivery_url: str
    delivery_description: str

class Rating(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_id: str
    rated_by: str
    rating: int  # 1-5 stars
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RatingCreate(BaseModel):
    rating: int
    comment: Optional[str] = None
    rated_by: str

# Routes
@api_router.get("/")
async def root():
    return {"message": "Make my day - Automation Marketplace API"}

# Order routes
@api_router.post("/orders", response_model=Order)
async def create_order(order_data: OrderCreate):
    order = Order(**order_data.dict())
    await db.orders.insert_one(order.dict())
    return order

@api_router.get("/orders", response_model=List[Order])
async def get_orders(status: Optional[OrderStatus] = None, category: Optional[OrderCategory] = None):
    filter_dict = {}
    if status:
        filter_dict["status"] = status
    if category:
        filter_dict["category"] = category
    
    orders = await db.orders.find(filter_dict).sort("created_at", -1).to_list(1000)
    return [Order(**order) for order in orders]

@api_router.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: str):
    order = await db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return Order(**order)

@api_router.post("/orders/{order_id}/claim")
async def claim_order(order_id: str, claim_data: OrderClaim):
    order = await db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order["status"] != OrderStatus.OPEN:
        raise HTTPException(status_code=400, detail="Order is not available for claiming")
    
    update_data = {
        "status": OrderStatus.CLAIMED,
        "claimed_by": claim_data.claimed_by,
        "claimed_at": datetime.utcnow()
    }
    
    await db.orders.update_one({"id": order_id}, {"$set": update_data})
    return {"message": "Order claimed successfully"}

@api_router.post("/orders/{order_id}/submit")
async def submit_order(order_id: str, submission: OrderSubmission):
    order = await db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order["status"] != OrderStatus.CLAIMED:
        raise HTTPException(status_code=400, detail="Order is not in claimed status")
    
    update_data = {
        "status": OrderStatus.SUBMITTED,
        "delivery_url": submission.delivery_url,
        "delivery_description": submission.delivery_description,
        "submitted_at": datetime.utcnow()
    }
    
    await db.orders.update_one({"id": order_id}, {"$set": update_data})
    return {"message": "Work submitted successfully"}

# Rating routes
@api_router.post("/orders/{order_id}/rate")
async def rate_order(order_id: str, rating_data: RatingCreate):
    if rating_data.rating < 1 or rating_data.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    order = await db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order["status"] != OrderStatus.SUBMITTED:
        raise HTTPException(status_code=400, detail="Order must be submitted before rating")
    
    # Check if user already rated this order
    existing_rating = await db.ratings.find_one({"order_id": order_id, "rated_by": rating_data.rated_by})
    if existing_rating:
        raise HTTPException(status_code=400, detail="You have already rated this order")
    
    # Create rating
    rating = Rating(order_id=order_id, **rating_data.dict())
    await db.ratings.insert_one(rating.dict())
    
    # Update order rating statistics
    new_total_score = order["total_rating_score"] + rating_data.rating
    new_rating_count = order["rating_count"] + 1
    new_average_rating = new_total_score / new_rating_count
    
    update_data = {
        "total_rating_score": new_total_score,
        "rating_count": new_rating_count,
        "average_rating": round(new_average_rating, 2)
    }
    
    # Check if order should be completed (4+ stars average with at least 3 ratings)
    if new_average_rating >= 4.0 and new_rating_count >= 3:
        update_data["status"] = OrderStatus.COMPLETED
        update_data["completed_at"] = datetime.utcnow()
    
    await db.orders.update_one({"id": order_id}, {"$set": update_data})
    
    return {"message": "Rating submitted successfully", "new_average": new_average_rating}

@api_router.get("/orders/{order_id}/ratings", response_model=List[Rating])
async def get_order_ratings(order_id: str):
    ratings = await db.ratings.find({"order_id": order_id}).sort("created_at", -1).to_list(1000)
    return [Rating(**rating) for rating in ratings]

# Stats routes
@api_router.get("/stats")
async def get_stats():
    total_orders = await db.orders.count_documents({})
    open_orders = await db.orders.count_documents({"status": OrderStatus.OPEN})
    completed_orders = await db.orders.count_documents({"status": OrderStatus.COMPLETED})
    total_value = await db.orders.aggregate([{"$group": {"_id": None, "total": {"$sum": "$payment_amount"}}}]).to_list(1)
    
    return {
        "total_orders": total_orders,
        "open_orders": open_orders, 
        "completed_orders": completed_orders,
        "total_value": total_value[0]["total"] if total_value else 0
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()