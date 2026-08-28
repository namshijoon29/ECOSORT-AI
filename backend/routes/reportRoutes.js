import { Router } from 'express';
import { create } from '../controllers/reportController.js';
import { asyncHandler } from '../middleware/asyncHandler.js';

const router = Router();
router.post('/', asyncHandler(create));
export default router;
