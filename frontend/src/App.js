import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CATEGORIES = {
  web_scraping: "Web Scraping",
  data_processing: "Data Processing", 
  api_integration: "API Integration",
  workflow_automation: "Workflow Automation",
  email_automation: "Email Automation",
  file_processing: "File Processing",
  database_automation: "Database Automation",
  other: "Other"
};

const STATUS_COLORS = {
  open: "bg-green-100 text-green-800",
  claimed: "bg-blue-100 text-blue-800", 
  in_progress: "bg-yellow-100 text-yellow-800",
  submitted: "bg-purple-100 text-purple-800",
  completed: "bg-gray-100 text-gray-800",
  rejected: "bg-red-100 text-red-800"
};

function App() {
  const [activeTab, setActiveTab] = useState('browse');
  const [orders, setOrders] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [newOrder, setNewOrder] = useState({
    title: '',
    description: '',
    category: 'other',
    payment_amount: '',
    requirements: [''],
    created_by: ''
  });

  useEffect(() => {
    fetchOrders();
    fetchStats();
  }, []);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/orders`);
      setOrders(response.data);
    } catch (error) {
      console.error('Error fetching orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleCreateOrder = async (e) => {
    e.preventDefault();
    try {
      const orderData = {
        ...newOrder,
        payment_amount: parseFloat(newOrder.payment_amount),
        requirements: newOrder.requirements.filter(req => req.trim() !== '')
      };
      
      await axios.post(`${API}/orders`, orderData);
      
      // Reset form
      setNewOrder({
        title: '',
        description: '',
        category: 'other',
        payment_amount: '',
        requirements: [''],
        created_by: ''
      });
      
      fetchOrders();
      fetchStats();
      setActiveTab('browse');
    } catch (error) {
      console.error('Error creating order:', error);
    }
  };

  const handleClaimOrder = async (orderId) => {
    const developerName = prompt('Enter your name/email to claim this order:');
    if (!developerName) return;

    try {
      await axios.post(`${API}/orders/${orderId}/claim`, {
        claimed_by: developerName
      });
      fetchOrders();
    } catch (error) {
      alert('Error claiming order: ' + error.response?.data?.detail);
    }
  };

  const handleSubmitWork = async (orderId) => {
    const deliveryUrl = prompt('Enter the URL where your work can be accessed (GitHub, Drive, etc.):');
    if (!deliveryUrl) return;
    
    const deliveryDescription = prompt('Describe your solution:');
    if (!deliveryDescription) return;

    try {
      await axios.post(`${API}/orders/${orderId}/submit`, {
        delivery_url: deliveryUrl,
        delivery_description: deliveryDescription
      });
      fetchOrders();
    } catch (error) {
      alert('Error submitting work: ' + error.response?.data?.detail);
    }
  };

  const handleRateOrder = async (orderId) => {
    const rating = prompt('Rate this automation (1-5 stars):');
    if (!rating || rating < 1 || rating > 5) return;
    
    const comment = prompt('Optional comment:');
    const ratedBy = prompt('Your name/email:');
    
    if (!ratedBy) return;

    try {
      await axios.post(`${API}/orders/${orderId}/rate`, {
        rating: parseInt(rating),
        comment: comment || undefined,
        rated_by: ratedBy
      });
      fetchOrders();
    } catch (error) {
      alert('Error rating order: ' + error.response?.data?.detail);
    }
  };

  const addRequirement = () => {
    setNewOrder(prev => ({
      ...prev,
      requirements: [...prev.requirements, '']
    }));
  };

  const updateRequirement = (index, value) => {
    setNewOrder(prev => ({
      ...prev,
      requirements: prev.requirements.map((req, i) => i === index ? value : req)
    }));
  };

  const removeRequirement = (index) => {
    setNewOrder(prev => ({
      ...prev,
      requirements: prev.requirements.filter((_, i) => i !== index)
    }));
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <h1 className="text-3xl font-bold text-gray-900">Make my day</h1>
              <span className="ml-3 text-sm text-gray-500">Automation Marketplace</span>
            </div>
            <div className="flex space-x-6 text-sm text-gray-600">
              <div>Total Orders: <span className="font-semibold">{stats.total_orders}</span></div>
              <div>Open: <span className="font-semibold text-green-600">{stats.open_orders}</span></div>
              <div>Completed: <span className="font-semibold text-blue-600">{stats.completed_orders}</span></div>
              <div>Total Value: <span className="font-semibold">${stats.total_value}</span></div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            <button
              onClick={() => setActiveTab('browse')}
              className={`py-4 px-2 border-b-2 font-medium text-sm ${
                activeTab === 'browse'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Browse Orders
            </button>
            <button
              onClick={() => setActiveTab('create')}
              className={`py-4 px-2 border-b-2 font-medium text-sm ${
                activeTab === 'create'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Post Order
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'browse' && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Available Automation Orders</h2>
              <button 
                onClick={fetchOrders}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
              >
                Refresh
              </button>
            </div>

            {loading ? (
              <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <p className="mt-2 text-gray-600">Loading orders...</p>
              </div>
            ) : (
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {orders.map((order) => (
                  <div key={order.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
                    <div className="flex justify-between items-start mb-3">
                      <h3 className="text-lg font-semibold text-gray-900 truncate">{order.title}</h3>
                      <span className={`px-2 py-1 text-xs rounded-full ${STATUS_COLORS[order.status]}`}>
                        {order.status.replace('_', ' ')}
                      </span>
                    </div>
                    
                    <div className="mb-3">
                      <span className="inline-block bg-gray-100 text-gray-700 px-2 py-1 text-xs rounded">
                        {CATEGORIES[order.category]}
                      </span>
                    </div>

                    <p className="text-gray-600 text-sm mb-4 line-clamp-3">{order.description}</p>
                    
                    <div className="flex justify-between items-center mb-4">
                      <div className="text-2xl font-bold text-green-600">${order.payment_amount}</div>
                      {order.average_rating > 0 && (
                        <div className="flex items-center">
                          <span className="text-yellow-400">★</span>
                          <span className="ml-1 text-sm text-gray-600">
                            {order.average_rating} ({order.rating_count})
                          </span>
                        </div>
                      )}
                    </div>

                    <div className="text-xs text-gray-500 mb-4">
                      Created by: {order.created_by} • {new Date(order.created_at).toLocaleDateString()}
                      {order.claimed_by && (
                        <div>Claimed by: {order.claimed_by}</div>
                      )}
                    </div>

                    {order.requirements.length > 0 && (
                      <div className="mb-4">
                        <p className="text-xs text-gray-500 mb-1">Requirements:</p>
                        <ul className="text-xs text-gray-600 space-y-1">
                          {order.requirements.slice(0, 3).map((req, idx) => (
                            <li key={idx}>• {req}</li>
                          ))}
                          {order.requirements.length > 3 && (
                            <li className="text-gray-400">... and {order.requirements.length - 3} more</li>
                          )}
                        </ul>
                      </div>
                    )}

                    {order.delivery_url && (
                      <div className="mb-4 p-3 bg-gray-50 rounded">
                        <p className="text-xs text-gray-500 mb-1">Delivered Work:</p>
                        <a href={order.delivery_url} target="_blank" rel="noopener noreferrer" 
                           className="text-blue-600 text-sm hover:underline">
                          View Solution
                        </a>
                        <p className="text-xs text-gray-600 mt-1">{order.delivery_description}</p>
                      </div>
                    )}

                    <div className="flex space-x-2">
                      {order.status === 'open' && (
                        <button
                          onClick={() => handleClaimOrder(order.id)}
                          className="flex-1 bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700"
                        >
                          Claim Order
                        </button>
                      )}
                      
                      {order.status === 'claimed' && order.claimed_by && (
                        <button
                          onClick={() => handleSubmitWork(order.id)}
                          className="flex-1 bg-green-600 text-white px-4 py-2 rounded text-sm hover:bg-green-700"
                        >
                          Submit Work
                        </button>
                      )}
                      
                      {order.status === 'submitted' && (
                        <button
                          onClick={() => handleRateOrder(order.id)}
                          className="flex-1 bg-yellow-600 text-white px-4 py-2 rounded text-sm hover:bg-yellow-700"
                        >
                          Rate & Test
                        </button>
                      )}
                      
                      {order.status === 'completed' && (
                        <div className="flex-1 text-center py-2 text-sm text-green-600 font-medium">
                          ✅ Work Available for Free!
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {orders.length === 0 && !loading && (
              <div className="text-center py-12">
                <p className="text-gray-500">No orders found. Be the first to post an automation request!</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'create' && (
          <div className="max-w-2xl mx-auto">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Post New Automation Order</h2>
            
            <form onSubmit={handleCreateOrder} className="bg-white rounded-lg shadow-md p-6">
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Your Name/Email
                </label>
                <input
                  type="text"
                  required
                  value={newOrder.created_by}
                  onChange={(e) => setNewOrder(prev => ({ ...prev, created_by: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="john@example.com"
                />
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Automation Title
                </label>
                <input
                  type="text"
                  required
                  value={newOrder.title}
                  onChange={(e) => setNewOrder(prev => ({ ...prev, title: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Automated Invoice Processing from Gmail"
                />
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  required
                  rows={4}
                  value={newOrder.description}
                  onChange={(e) => setNewOrder(prev => ({ ...prev, description: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Describe what automation you need, expected input/output, and any specific requirements..."
                />
              </div>

              <div className="grid grid-cols-2 gap-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Category
                  </label>
                  <select
                    value={newOrder.category}
                    onChange={(e) => setNewOrder(prev => ({ ...prev, category: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {Object.entries(CATEGORIES).map(([key, label]) => (
                      <option key={key} value={key}>{label}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Payment Amount ($)
                  </label>
                  <input
                    type="number"
                    min="1"
                    step="0.01"
                    required
                    value={newOrder.payment_amount}
                    onChange={(e) => setNewOrder(prev => ({ ...prev, payment_amount: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="100.00"
                  />
                </div>
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Requirements
                </label>
                {newOrder.requirements.map((req, index) => (
                  <div key={index} className="flex mb-2">
                    <input
                      type="text"
                      value={req}
                      onChange={(e) => updateRequirement(index, e.target.value)}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="e.g., Must handle PDF files"
                    />
                    {newOrder.requirements.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removeRequirement(index)}
                        className="ml-2 px-3 py-2 text-red-600 hover:bg-red-50 rounded"
                      >
                        ✕
                      </button>
                    )}
                  </div>
                ))}
                <button
                  type="button"
                  onClick={addRequirement}
                  className="text-blue-600 text-sm hover:underline"
                >
                  + Add Requirement
                </button>
              </div>

              <div className="bg-blue-50 p-4 rounded-md mb-6">
                <p className="text-sm text-blue-700">
                  <strong>How it works:</strong> Post your order → Developer claims it → They deliver the automation → 
                  Community rates it → When it reaches 4+ stars (minimum 3 ratings), payment is released and the 
                  automation becomes free for everyone!
                </p>
              </div>

              <button
                type="submit"
                className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 font-medium"
              >
                Post Order
              </button>
            </form>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;