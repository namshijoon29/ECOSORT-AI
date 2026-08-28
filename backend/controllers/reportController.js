import { createReport } from '../services/reportService.js';

export async function create(req, res) {
  const { userId, problemType, description, location, imageUrl } = req.body;
  if (!userId || !problemType) return res.status(400).json({ success: false, message: 'userId and problemType are required.' });
  const report = await createReport({ user: userId, problemType, description, location, imageUrl });
  res.status(201).json({ success: true, report });
}
