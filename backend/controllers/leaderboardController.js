import { getLeaderboard } from '../services/leaderboardService.js';

export async function leaderboard(req, res) {
  res.json({ success: true, leaderboard: await getLeaderboard(req.query.userType) });
}
