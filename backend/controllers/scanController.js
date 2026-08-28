import Scan from '../models/Scan.js';
import User from '../models/User.js';
import { classifyWasteImage } from '../services/visionService.js';
import { applySortingReward } from '../services/rewardService.js';
import { evaluateBin, normalizeObjects } from '../services/wasteService.js';
import { hasValidImageSignature } from '../middleware/uploadMiddleware.js';

export async function analyzeImage(req, res) {
  if (!req.file) return res.status(400).json({ success: false, message: 'Upload an image using the image field.' });
  if (!hasValidImageSignature(req.file.buffer, req.file.mimetype)) return res.status(400).json({ success: false, message: 'The uploaded file is not a valid image.' });
  const user = await User.findById(req.body.userId);
  if (!user) return res.status(404).json({ success: false, message: 'User not found.' });
  const objects = normalizeObjects(await classifyWasteImage(req.file));
  const scan = await Scan.create({ user: user._id, imageName: req.file.originalname, imageMimeType: req.file.mimetype, objects });
  res.status(201).json({ success: true, mode: 'VISION_AI', scanId: scan._id, objects });
}

export async function submitSort(req, res) {
  const scan = await Scan.findById(req.params.id);
  if (!scan) return res.status(404).json({ success: false, message: 'Scan not found.' });
  if (scan.correct) return res.status(409).json({ success: false, message: 'This scan was already rewarded.' });
  const correct = evaluateBin(scan.objects, req.body.selectedBin);
  const reward = await applySortingReward(scan.user, correct, scan.objects.length);
  scan.selectedBin = String(req.body.selectedBin || '').toUpperCase();
  scan.correct = correct;
  scan.xpAwarded = reward.xp;
  scan.creditsAwarded = reward.credits;
  await scan.save();
  res.json({ success: true, correct, reward, scan });
}

export async function getScan(req, res) {
  const scan = await Scan.findById(req.params.id).populate('user', 'username userType');
  if (!scan) return res.status(404).json({ success: false, message: 'Scan not found.' });
  res.json({ success: true, scan });
}
