import { Router } from 'express';
import { listRewards, redeem } from '../controllers/rewardController.js';
import { asyncHandler } from '../middleware/asyncHandler.js';

const router = Router();
router.get('/', asyncHandler(listRewards));
router.post('/:rewardId/redeem', asyncHandler(redeem));
export default router;
