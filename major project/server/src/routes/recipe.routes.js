import express from 'express';
const router = express.Router();

// Define recipe routes
router.get('/recipes', (req, res) => {
  res.json({ message: 'Get all recipes' });
});

router.get('/recipes/:id', (req, res) => {
  res.json({ message: `Get recipe with id: ${req.params.id}` });
});

router.post('/recipes', (req, res) => {
  res.json({ message: 'Create new recipe', data: req.body });
});

// Export router
export default router;