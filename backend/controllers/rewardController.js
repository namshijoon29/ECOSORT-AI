import Reward from '../models/Reward.js';
import { redeemReward } from '../services/rewardService.js';

export async function listRewards(req, res) {
  const userType = String(req.query.userType || '').toUpperCase();
  const filter = userType ? { active: true, $or: [{ userType: 'BOTH' }, { userType }] } : { active: true };
  res.json({ success: true, rewards: await Reward.find(filter).sort({ cost: 1 }).lean() });
}

export async function redeem(req, res) {
  const reward = await Reward.findOne({ _id: req.params.rewardId, active: true });
  if (!reward) return res.status(404).json({ success: false, message: 'Reward not found.' });
  const user = await redeemReward(req.body.userId, reward.cost);
  res.json({ success: true, reward, creditsRemaining: user.credits });
}
