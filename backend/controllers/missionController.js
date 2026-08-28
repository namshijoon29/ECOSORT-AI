import { listMissions } from '../services/missionService.js';

export async function getMissions(req, res) {
  res.json({ success: true, missions: await listMissions(req.query.userType) });
}
