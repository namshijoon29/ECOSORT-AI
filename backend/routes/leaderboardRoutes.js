import { Router } from 'express';
import { leaderboard } from '../controllers/leaderboardController.js';
import { asyncHandler } from '../middleware/asyncHandler.js';

const router = Router();
router.get('/', asyncHandler(leaderboard));
export default router;
