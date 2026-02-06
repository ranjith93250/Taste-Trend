import axios from 'axios';

const TREND_SERVICE_URL = 'http://localhost:8003';

/**
 * Get trending dishes from the trend analysis service
 * @returns {Promise<Object>} - Returns trending dishes from the ML service
 */
async function getTrendingDishes() {
    try {
        const response = await axios.get(`${TREND_SERVICE_URL}/trend`);
        
        return response.data;
    } catch (error) {
        console.error('Error calling trend service:', error.message);
        throw new Error(`Failed to get trending dishes: ${error.message}`);
    }
}

export { getTrendingDishes };
