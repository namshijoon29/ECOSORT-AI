import User from '../models/User.js';

export async function getLeaderboard(userType) {
  const filter = userType ? { userType: String(userType).toUpperCase() } : {};
  return User.find(filter).select('username userType leaderboardScore xp credits').sort({ leaderboardScore: -1 }).limit(100).lean();
}
