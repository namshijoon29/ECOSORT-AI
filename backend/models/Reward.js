import mongoose from 'mongoose';

const rewardSchema = new mongoose.Schema({
  name: { type: String, required: true },
  description: String,
  cost: { type: Number, required: true, min: 0 },
  userType: { type: String, enum: ['STUDENT', 'RESIDENT', 'BOTH'], default: 'BOTH' },
  active: { type: Boolean, default: true },
}, { timestamps: true });

export default mongoose.model('Reward', rewardSchema);
