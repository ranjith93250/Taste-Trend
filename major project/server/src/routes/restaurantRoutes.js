import express from 'express';
const router = express.Router();

// Test route
router.get('/test', (req, res) => {
  res.json({ message: 'Restaurant route working' });
});

export default router;