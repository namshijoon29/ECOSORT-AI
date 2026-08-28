import { Router } from 'express';
import { getUser, login, register, updateUser } from '../controllers/authController.js';
import { asyncHandler } from '../middleware/asyncHandler.js';

const router = Router();
router.post('/register', asyncHandler(register));
router.post('/login', asyncHandler(login));
router.get('/user/:id', asyncHandler(getUser));
router.put('/user/:id', asyncHandler(updateUser));
export default router;
