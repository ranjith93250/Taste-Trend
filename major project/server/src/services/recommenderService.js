import axios from 'axios';

const RECOMMENDER_SERVICE_URL = 'http://localhost:8001';

/**
 * Get food recommendations for a user
 * @param {number} userId - The user ID to get recommendations for
 * @returns {Promise<Object>} - Returns recommendations from the ML service
 */
async function getRecommendations(userId) {
    try {
        const response = await axios.post(`${RECOMMENDER_SERVICE_URL}/recommend`, {
            user_id: userId
        });
        
        return response.data;
    } catch (error) {
        console.error('Error calling recommender service:', error.message);
        throw new Error(`Failed to get recommendations: ${error.message}`);
    }
}

export { getRecommendations };
