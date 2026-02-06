import express from 'express';
import { recommend } from '../controllers/recommenderController.js';
const router = express.Router();

// POST /api/recommend
router.post('/', recommend);

export default router;
