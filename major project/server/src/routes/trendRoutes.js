import express from 'express';
import { trend } from '../controllers/trendController.js';
const router = express.Router();

// GET /api/trend
router.get('/', trend);

export default router;
