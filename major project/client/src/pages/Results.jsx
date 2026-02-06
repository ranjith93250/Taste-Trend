import React, { useEffect, useState } from 'react';
import { analyzeSentiment, getRecommendations, getTrendingDishes } from '../utils/api';

const Results = () => {
  // State for user inputs
  const [userId, setUserId] = useState('');
  const [review, setReview] = useState('');
  
  // State for API results
  const [recommendations, setRecommendations] = useState([]);
  const [sentiment, setSentiment] = useState('');
  const [trending, setTrending] = useState([]);
  
  // State for loading and error handling
  const [loading, setLoading] = useState({
    recommendations: false,
    sentiment: false,
    trending: false
  });
  const [error, setError] = useState('');

  // Load trending dishes on component mount
  useEffect(() => {
    loadTrending();
  }, []);

  // Function to get recommendations
  const handleRecommendation = async () => {
    if (!userId) {
      setError('Please enter a user ID');
      return;
    }
    
    setLoading(prev => ({ ...prev, recommendations: true }));
    setError('');
    
    try {
      const result = await getRecommendations(parseInt(userId));
      setRecommendations(result.recommendations || []);
    } catch (err) {
      setError('Failed to fetch recommendations');
      console.error('Recommendation error:', err);
    } finally {
      setLoading(prev => ({ ...prev, recommendations: false }));
    }
  };

  // Function to analyze sentiment
  const handleSentiment = async () => {
    if (!review.trim()) {
      setError('Please enter a review text');
      return;
    }
    
    setLoading(prev => ({ ...prev, sentiment: true }));
    setError('');
    
    try {
      const result = await analyzeSentiment(review);
      setSentiment(result.sentiment || '');
    } catch (err) {
      setError('Failed to analyze sentiment');
      console.error('Sentiment error:', err);
    } finally {
      setLoading(prev => ({ ...prev, sentiment: false }));
    }
  };

  // Function to load trending dishes
  const loadTrending = async () => {
    setLoading(prev => ({ ...prev, trending: true }));
    
    try {
      const result = await getTrendingDishes();
      setTrending(result.trending_dishes || []);
    } catch (err) {
      setError('Failed to fetch trending dishes');
      console.error('Trending error:', err);
    } finally {
      setLoading(prev => ({ ...prev, trending: false }));
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-center mb-8 text-gray-800">
          API Testing Results
        </h1>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recommendations Section */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-700">
              Food Recommendations
            </h2>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-600 mb-2">
                User ID:
              </label>
              <div className="flex gap-2">
                <input
                  type="number"
                  value={userId}
                  onChange={(e) => setUserId(e.target.value)}
                  placeholder="Enter user ID (e.g., 123)"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={handleRecommendation}
                  disabled={loading.recommendations}
                  className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading.recommendations ? 'Loading...' : 'Get Recommendations'}
                </button>
              </div>
            </div>

            <div className="mt-4">
              <h3 className="text-lg font-medium text-gray-600 mb-2">Results:</h3>
              {recommendations.length > 0 ? (
                <ul className="list-disc list-inside space-y-1">
                  {recommendations.map((dish, index) => (
                    <li key={index} className="text-gray-700">
                      {dish}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500 italic">No recommendations yet</p>
              )}
            </div>
          </div>

          {/* Sentiment Analysis Section */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-700">
              Sentiment Analysis
            </h2>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-600 mb-2">
                Review Text:
              </label>
              <div className="space-y-2">
                <textarea
                  value={review}
                  onChange={(e) => setReview(e.target.value)}
                  placeholder="Enter your review (e.g., 'This food is amazing!')"
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={handleSentiment}
                  disabled={loading.sentiment}
                  className="w-full px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading.sentiment ? 'Analyzing...' : 'Analyze Sentiment'}
                </button>
              </div>
            </div>

            <div className="mt-4">
              <h3 className="text-lg font-medium text-gray-600 mb-2">Result:</h3>
              {sentiment ? (
                <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
                  sentiment === 'positive' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {sentiment.charAt(0).toUpperCase() + sentiment.slice(1)}
                </div>
              ) : (
                <p className="text-gray-500 italic">No sentiment analyzed yet</p>
              )}
            </div>
          </div>
        </div>

        {/* Trending Dishes Section */}
        <div className="mt-8 bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-700">
            Trending Dishes
          </h2>
          
          {loading.trending ? (
            <p className="text-gray-500">Loading trending dishes...</p>
          ) : (
            <div>
              <p className="text-sm text-gray-600 mb-3">
                These dishes are currently trending (loaded automatically):
              </p>
              {trending.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {trending.map((dish, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-medium"
                    >
                      {dish}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 italic">No trending dishes available</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Results;
