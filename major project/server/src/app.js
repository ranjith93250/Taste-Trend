import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

// Create Express app
const app = express();

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.get('/', (req, res) => {
  res.send('TasteTrend API is running...');
});

// Import routes
import routes from './routes/index.js';
import restaurantRoutes from './routes/restaurantRoutes.js';
import recommenderRoutes from './routes/recommenderRoutes.js';
import sentimentRoutes from './routes/sentimentRoutes.js';
import trendRoutes from './routes/trendRoutes.js';

// Use routes
app.use(routes);
app.use('/api/restaurants', restaurantRoutes);
app.use('/api/recommend', recommenderRoutes);
app.use('/api/sentiment', sentimentRoutes);
app.use('/api/trend', trendRoutes);

// Error handling middleware
app.use((err, req, res, next) => {
  const statusCode = res.statusCode === 200 ? 500 : res.statusCode;
  res.status(statusCode);
  res.json({
    message: err.message,
    stack: process.env.NODE_ENV === 'production' ? null : err.stack,
  });
});

export default app;