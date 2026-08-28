import { Router } from 'express';
import { getMissions } from '../controllers/missionController.js';
import { asyncHandler } from '../middleware/asyncHandler.js';

const router = Router();
router.get('/', asyncHandler(getMissions));
export default router;
