import { Router } from 'express';
import { messageChat, startChat } from '../controllers/chatController.js';
import { asyncHandler } from '../middleware/asyncHandler.js';

const router = Router();
router.post('/start', asyncHandler(startChat));
router.post('/message', asyncHandler(messageChat));
export default router;
