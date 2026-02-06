import axios from 'axios';

const SENTIMENT_SERVICE_URL = 'http://localhost:8002';

/**
 * Analyze sentiment of a review text
 * @param {string} review - The review text to analyze
 * @returns {Promise<Object>} - Returns sentiment analysis result from the ML service
 */
async function analyzeSentiment(review) {
    try {
        const response = await axios.post(`${SENTIMENT_SERVICE_URL}/analyze`, {
            review: review
        });
        
        return response.data;
    } catch (error) {
        console.error('Error calling sentiment service:', error.message);
        throw new Error(`Failed to analyze sentiment: ${error.message}`);
    }
}

export { analyzeSentiment };
