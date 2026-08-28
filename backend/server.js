import dotenv from 'dotenv';
import path from 'node:path';
dotenv.config({ path: path.resolve(process.cwd(), '.env') });
dotenv.config({ path: path.resolve(process.cwd(), '../.env'), override: false });
import cors from 'cors';
import express from 'express';
import { connectDatabase } from './config/db.js';
import authRoutes from './routes/authRoutes.js';
import scanRoutes from './routes/scanRoutes.js';
import rewardRoutes from './routes/rewardRoutes.js';
import missionRoutes from './routes/missionRoutes.js';
import leaderboardRoutes from './routes/leaderboardRoutes.js';
import reportRoutes from './routes/reportRoutes.js';
import chatRoutes from './routes/chatRoutes.js';
import { errorHandler, notFoundHandler } from './middleware/errorMiddleware.js';

const app = express();
const port = Number(process.env.PORT || 5000);
const allowedOrigins = process.env.CLIENT_ORIGIN ? process.env.CLIENT_ORIGIN.split(',').map((origin) => origin.trim()) : true;

app.use(cors({ origin: allowedOrigins }));
app.use(express.json({ limit: '1mb' }));
app.get('/api/health', (req, res) => res.json({ success: true, message: 'EcoSort AI backend is running' }));
app.use('/api/auth', authRoutes);
app.use('/api/scans', scanRoutes);
app.use('/api/rewards', rewardRoutes);
app.use('/api/missions', missionRoutes);
app.use('/api/leaderboards', leaderboardRoutes);
app.use('/api/reports', reportRoutes);
app.use('/api/chat', chatRoutes);
app.use(notFoundHandler);
app.use(errorHandler);

async function start() {
  await connectDatabase();
  app.listen(port, () => console.log(`EcoSort AI backend listening on http://localhost:${port}`));
}

start().catch((error) => {
  console.error(`Backend startup failed: ${error.message}`);
  process.exit(1);
});

export default app;
