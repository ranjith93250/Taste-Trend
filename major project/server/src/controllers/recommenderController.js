import { getRecommendations } from '../services/recommenderService.js';

/**
 * Get food recommendations for a user
 * POST /api/recommend
 */
async function recommend(req, res) {
    try {
        const { userId } = req.body;
        
        if (!userId) {
            return res.status(400).json({ error: 'User ID is required' });
        }
        
        const recommendations = await getRecommendations(userId);
        res.json(recommendations);
    } catch (error) {
        console.error('Error in recommend controller:', error.message);
        res.status(500).json({ error: 'Failed to fetch recommendations' });
    }
}

export { recommend };
