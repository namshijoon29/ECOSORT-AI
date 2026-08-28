import { Router } from 'express';
import { analyzeImage, getScan, submitSort } from '../controllers/scanController.js';
import { uploadWasteImage } from '../middleware/uploadMiddleware.js';
import { asyncHandler } from '../middleware/asyncHandler.js';

const router = Router();
router.post('/analyze', uploadWasteImage, asyncHandler(analyzeImage));
router.post('/:id/sort', asyncHandler(submitSort));
router.get('/:id', asyncHandler(getScan));
export default router;
