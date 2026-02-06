import express from 'express';
const router = express.Router();

// Define user routes
router.get('/users', (req, res) => {
  res.json({ message: 'Get all users' });
});

router.get('/users/:id', (req, res) => {
  res.json({ message: `Get user with id: ${req.params.id}` });
});

router.post('/users', (req, res) => {
  res.json({ message: 'Create new user', data: req.body });
});

// Export router
export default router;