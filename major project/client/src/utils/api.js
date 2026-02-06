import axios from 'axios';

// Set base URL for all API calls
const baseURL = 'http://localhost:5000/api';

// Create axios instance with base configuration
const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Get food recommendations for a user
 * @param {number} userId - The user ID to get recommendations for
 * @returns {Promise<Object>} - Returns recommendations from the backend
 */
export const getRecommendations = async (userId) => {
  try {
    const response = await api.post('/recommend', { userId });
    return response.data;
  } catch (error) {
    console.error('Error fetching recommendations:', error.message);
    throw error;
  }
};

/**
 * Analyze sentiment of a review text
 * @param {string} review - The review text to analyze
 * @returns {Promise<Object>} - Returns sentiment analysis result
 */
export const analyzeSentiment = async (review) => {
  try {
    const response = await api.post('/sentiment/analyze', { review });
    return response.data;
  } catch (error) {
    console.error('Error analyzing sentiment:', error.message);
    throw error;
  }
};

/**
 * Get trending dishes
 * @returns {Promise<Object>} - Returns trending dishes from the backend
 */
export const getTrendingDishes = async () => {
  try {
    const response = await api.get('/trend');
    return response.data;
  } catch (error) {
    console.error('Error fetching trending dishes:', error.message);
    throw error;
  }
};

// Export the axios instance for custom requests if needed
export default api;
