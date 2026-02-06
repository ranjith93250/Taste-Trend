import express from 'express';
import userRoutes from './user.routes.js';
import recipeRoutes from './recipe.routes.js';
import restaurantRoutes from './restaurantRoutes.js';
const router = express.Router();

// Define routes
router.get('/api', (req, res) => {
  res.json({ message: 'Welcome to TasteTrend API!' });
});

// Use route modules
router.use('/api', userRoutes);
router.use('/api', recipeRoutes);
router.use('/api', restaurantRoutes);

// Export router
export default router;