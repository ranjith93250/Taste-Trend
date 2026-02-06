import { analyzeSentiment } from '../services/sentimentService.js';

/**
 * Analyze sentiment of a review
 * POST /api/sentiment/analyze
 */
async function analyze(req, res) {
    try {
        const { review } = req.body;
        
        if (!review) {
            return res.status(400).json({ error: 'Review text is required' });
        }
        
        const sentiment = await analyzeSentiment(review);
        res.json(sentiment);
    } catch (error) {
        console.error('Error in analyze controller:', error.message);
        res.status(500).json({ error: 'Failed to analyze sentiment' });
    }
}

export { analyze };
