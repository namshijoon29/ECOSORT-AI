import mongoose from 'mongoose';

const userSchema = new mongoose.Schema({
  userType: { type: String, enum: ['STUDENT', 'RESIDENT'], required: true },
  username: { type: String, required: true, trim: true },
  registrationNumber: { type: String, unique: true, sparse: true, trim: true },
  employeeId: { type: String, unique: true, sparse: true, trim: true },
  collegeName: String,
  campus: String,
  hostel: String,
  block: String,
  roomNumber: String,
  department: String,
  year: String,
  buildingName: String,
  flatNumber: String,
  tower: String,
  floor: String,
  area: String,
  city: String,
  avatar: String,
  xp: { type: Number, default: 0, min: 0 },
  level: { type: Number, default: 1, min: 1 },
  credits: { type: Number, default: 0, min: 0 },
  streak: { type: Number, default: 0, min: 0 },
  badges: { type: [String], default: [] },
  scanCount: { type: Number, default: 0, min: 0 },
  correctSortCount: { type: Number, default: 0, min: 0 },
  leaderboardScore: { type: Number, default: 0, min: 0 },
  missionProgress: [{
    mission: { type: mongoose.Schema.Types.ObjectId, ref: 'Mission' },
    progress: { type: Number, default: 0 },
    completed: { type: Boolean, default: false },
  }],
}, { timestamps: true });

export default mongoose.model('User', userSchema);
