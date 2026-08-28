import mongoose from 'mongoose';

const missionSchema = new mongoose.Schema({
  title: { type: String, required: true },
  description: String,
  target: { type: Number, required: true, min: 1 },
  rewardXp: { type: Number, default: 0 },
  rewardCredits: { type: Number, default: 0 },
  userType: { type: String, enum: ['STUDENT', 'RESIDENT', 'BOTH'], default: 'BOTH' },
  active: { type: Boolean, default: true },
}, { timestamps: true });

export default mongoose.model('Mission', missionSchema);
