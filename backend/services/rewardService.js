import User from '../models/User.js';
import Mission from '../models/Mission.js';

export async function applySortingReward(userId, correct, objectCount = 1) {
  if (!correct) return { xp: 0, credits: 0 };
  const xp = 20 * objectCount;
  const credits = 10 * objectCount;
  const user = await User.findByIdAndUpdate(userId, {
    $inc: { xp, credits, scanCount: 1, correctSortCount: 1, leaderboardScore: xp },
  }, { new: true });
  if (!user) throw Object.assign(new Error('User not found.'), { statusCode: 404, publicMessage: 'User not found.' });
  user.level = Math.max(1, Math.floor(user.xp / 1000) + 1);
  const missions = await Mission.find({ active: true, $or: [{ userType: 'BOTH' }, { userType: user.userType }] }).lean();
  for (const mission of missions) {
    const progress = user.missionProgress.find((entry) => String(entry.mission) === String(mission._id));
    if (progress) {
      if (!progress.completed) progress.progress = Math.min(mission.target, progress.progress + objectCount);
      progress.completed = progress.progress >= mission.target;
    } else {
      user.missionProgress.push({ mission: mission._id, progress: Math.min(mission.target, objectCount), completed: objectCount >= mission.target });
    }
  }
  await user.save();
  return { xp, credits, level: user.level };
}

export async function redeemReward(userId, cost) {
  const user = await User.findOneAndUpdate({ _id: userId, credits: { $gte: cost } }, { $inc: { credits: -cost } }, { new: true });
  if (!user) throw Object.assign(new Error('Insufficient credits or user not found.'), { statusCode: 400, publicMessage: 'Insufficient credits or user not found.' });
  return user;
}
