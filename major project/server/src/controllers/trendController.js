import { getTrendingDishes } from '../services/trendService.js';

/**
 * Get trending dishes
 * GET /api/trend/trend
 */
async function trend(req, res) {
    try {
        const trendingDishes = await getTrendingDishes();
        res.json(trendingDishes);
    } catch (error) {
        console.error('Error in trend controller:', error.message);
        res.status(500).json({ error: 'Failed to fetch trending dishes' });
    }
}

export { trend };
