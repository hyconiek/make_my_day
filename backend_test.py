#!/usr/bin/env python3
import requests
import json
import time
import uuid
import os
from dotenv import load_dotenv
import sys

# Load environment variables from frontend/.env to get the backend URL
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

print(f"Testing backend API at: {API_URL}")

# Test data
test_order = {
    "title": "Automate Email Sorting",
    "description": "Create a script that automatically sorts emails into folders based on content and sender",
    "category": "email_automation",
    "payment_amount": 75.50,
    "requirements": ["Python script", "Gmail API integration", "Documentation"],
    "created_by": "test.user@example.com"
}

test_claim = {
    "claimed_by": "developer@example.com"
}

test_submission = {
    "delivery_url": "https://github.com/developer/email-automation",
    "delivery_description": "Completed email automation script with Gmail API integration and detailed documentation"
}

test_ratings = [
    {"rating": 5, "comment": "Excellent work, exactly what I needed!", "rated_by": "rater1@example.com"},
    {"rating": 4, "comment": "Good job, works well", "rated_by": "rater2@example.com"},
    {"rating": 3, "comment": "Satisfactory, but could be improved", "rated_by": "rater3@example.com"},
    {"rating": 5, "comment": "Perfect solution!", "rated_by": "rater4@example.com"}
]

# Helper function to print test results
def print_test_result(test_name, success, response=None, error=None):
    if success:
        print(f"✅ {test_name}: PASSED")
        if response:
            print(f"   Response: {response}")
    else:
        print(f"❌ {test_name}: FAILED")
        if error:
            print(f"   Error: {error}")
        if response:
            print(f"   Response: {response}")
    print("-" * 80)

# Test 1: Create a new order
def test_create_order():
    try:
        response = requests.post(f"{API_URL}/orders", json=test_order)
        response.raise_for_status()
        order_data = response.json()
        print_test_result("Create Order", True, order_data)
        return order_data
    except Exception as e:
        print_test_result("Create Order", False, error=str(e))
        return None

# Test 2: Get all orders
def test_get_orders():
    try:
        response = requests.get(f"{API_URL}/orders")
        response.raise_for_status()
        orders = response.json()
        print_test_result("Get All Orders", True, f"Retrieved {len(orders)} orders")
        return orders
    except Exception as e:
        print_test_result("Get All Orders", False, error=str(e))
        return None

# Test 3: Get orders with filter
def test_get_filtered_orders():
    try:
        # Test filtering by status
        response = requests.get(f"{API_URL}/orders?status=open")
        response.raise_for_status()
        open_orders = response.json()
        
        # Test filtering by category
        response = requests.get(f"{API_URL}/orders?category=email_automation")
        response.raise_for_status()
        email_orders = response.json()
        
        print_test_result("Get Filtered Orders", True, 
                          f"Open orders: {len(open_orders)}, Email automation orders: {len(email_orders)}")
        return True
    except Exception as e:
        print_test_result("Get Filtered Orders", False, error=str(e))
        return False

# Test 4: Get specific order
def test_get_order(order_id):
    try:
        response = requests.get(f"{API_URL}/orders/{order_id}")
        response.raise_for_status()
        order = response.json()
        print_test_result("Get Specific Order", True, order)
        return order
    except Exception as e:
        print_test_result("Get Specific Order", False, error=str(e))
        return None

# Test 5: Claim an order
def test_claim_order(order_id):
    try:
        response = requests.post(f"{API_URL}/orders/{order_id}/claim", json=test_claim)
        response.raise_for_status()
        result = response.json()
        print_test_result("Claim Order", True, result)
        return True
    except Exception as e:
        print_test_result("Claim Order", False, error=str(e))
        return False

# Test 6: Test claiming an already claimed order (should fail)
def test_claim_already_claimed_order(order_id):
    try:
        response = requests.post(f"{API_URL}/orders/{order_id}/claim", 
                                json={"claimed_by": "another.developer@example.com"})
        if response.status_code == 400:
            print_test_result("Claim Already Claimed Order", True, 
                             "Correctly rejected claiming an already claimed order")
            return True
        else:
            print_test_result("Claim Already Claimed Order", False, 
                             f"Expected 400 error, got {response.status_code}")
            return False
    except Exception as e:
        print_test_result("Claim Already Claimed Order", False, error=str(e))
        return False

# Test 7: Submit work for an order
def test_submit_order(order_id):
    try:
        response = requests.post(f"{API_URL}/orders/{order_id}/submit", json=test_submission)
        response.raise_for_status()
        result = response.json()
        print_test_result("Submit Order", True, result)
        return True
    except Exception as e:
        print_test_result("Submit Order", False, error=str(e))
        return False

# Test 8: Rate an order
def test_rate_order(order_id, rating_data):
    try:
        response = requests.post(f"{API_URL}/orders/{order_id}/rate", json=rating_data)
        response.raise_for_status()
        result = response.json()
        print_test_result(f"Rate Order ({rating_data['rated_by']})", True, result)
        return True
    except Exception as e:
        print_test_result(f"Rate Order ({rating_data['rated_by']})", False, error=str(e))
        return False

# Test 9: Test rating an order twice with the same user (should fail)
def test_rate_order_twice(order_id, rating_data):
    try:
        response = requests.post(f"{API_URL}/orders/{order_id}/rate", json=rating_data)
        if response.status_code == 400:
            print_test_result("Rate Order Twice", True, 
                             "Correctly rejected rating an order twice by the same user")
            return True
        else:
            print_test_result("Rate Order Twice", False, 
                             f"Expected 400 error, got {response.status_code}")
            return False
    except Exception as e:
        print_test_result("Rate Order Twice", False, error=str(e))
        return False

# Test 10: Get order ratings
def test_get_order_ratings(order_id):
    try:
        response = requests.get(f"{API_URL}/orders/{order_id}/ratings")
        response.raise_for_status()
        ratings = response.json()
        print_test_result("Get Order Ratings", True, f"Retrieved {len(ratings)} ratings")
        return ratings
    except Exception as e:
        print_test_result("Get Order Ratings", False, error=str(e))
        return None

# Test 11: Verify order completion
def test_verify_order_completion(order_id):
    try:
        response = requests.get(f"{API_URL}/orders/{order_id}")
        response.raise_for_status()
        order = response.json()
        
        if order["status"] == "completed" and order["average_rating"] >= 4.0 and order["rating_count"] >= 3:
            print_test_result("Verify Order Completion", True, 
                             f"Order completed with average rating {order['average_rating']} from {order['rating_count']} ratings")
            return True
        else:
            print_test_result("Verify Order Completion", False, 
                             f"Order status: {order['status']}, Average rating: {order['average_rating']}, Rating count: {order['rating_count']}")
            return False
    except Exception as e:
        print_test_result("Verify Order Completion", False, error=str(e))
        return False

# Test 12: Get statistics
def test_get_stats():
    try:
        response = requests.get(f"{API_URL}/stats")
        response.raise_for_status()
        stats = response.json()
        print_test_result("Get Statistics", True, stats)
        return stats
    except Exception as e:
        print_test_result("Get Statistics", False, error=str(e))
        return None

# Test 13: Test invalid rating value
def test_invalid_rating(order_id):
    try:
        invalid_rating = {
            "rating": 6,  # Invalid rating (should be 1-5)
            "comment": "This rating is too high",
            "rated_by": "invalid.rater@example.com"
        }
        
        response = requests.post(f"{API_URL}/orders/{order_id}/rate", json=invalid_rating)
        if response.status_code == 400:
            print_test_result("Invalid Rating Value", True, 
                             "Correctly rejected rating value outside 1-5 range")
            return True
        else:
            print_test_result("Invalid Rating Value", False, 
                             f"Expected 400 error, got {response.status_code}")
            return False
    except Exception as e:
        print_test_result("Invalid Rating Value", False, error=str(e))
        return False

# Run all tests
def run_tests():
    print("\n" + "=" * 80)
    print("STARTING BACKEND API TESTS")
    print("=" * 80 + "\n")
    
    # Test order creation and retrieval
    created_order = test_create_order()
    if not created_order:
        print("❌ Cannot continue tests without a valid order")
        return False
    
    order_id = created_order["id"]
    
    # Test order listing and filtering
    all_orders = test_get_orders()
    test_get_filtered_orders()
    
    # Test getting specific order
    specific_order = test_get_order(order_id)
    
    # Test order lifecycle
    if test_claim_order(order_id):
        # Test error case: claiming already claimed order
        test_claim_already_claimed_order(order_id)
        
        if test_submit_order(order_id):
            # Test rating system
            test_invalid_rating(order_id)
            
            # Apply multiple ratings to test completion logic
            for i, rating in enumerate(test_ratings):
                if test_rate_order(order_id, rating):
                    # After first rating, test rating twice with same user
                    if i == 0:
                        test_rate_order_twice(order_id, rating)
            
            # Get ratings
            test_get_order_ratings(order_id)
            
            # Verify order completion
            test_verify_order_completion(order_id)
    
    # Test statistics
    test_get_stats()
    
    print("\n" + "=" * 80)
    print("BACKEND API TESTS COMPLETED")
    print("=" * 80 + "\n")
    return True

if __name__ == "__main__":
    run_tests()