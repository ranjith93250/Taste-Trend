import express from 'express';
import { analyze } from '../controllers/sentimentController.js';
const router = express.Router();

// POST /api/sentiment/analyze
router.post('/analyze', analyze);

export default router;
