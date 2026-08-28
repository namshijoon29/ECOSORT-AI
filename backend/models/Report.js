import mongoose from 'mongoose';

const reportSchema = new mongoose.Schema({
  user: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  problemType: { type: String, enum: ['OVERFLOWING_BIN', 'MISSED_COLLECTION', 'WRONG_SEGREGATION', 'WASTE_HOTSPOT', 'HAZARDOUS_WASTE'], required: true },
  description: String,
  location: String,
  imageUrl: String,
  ticketId: { type: String, unique: true },
  status: { type: String, enum: ['REPORTED', 'AI_CLASSIFIED', 'ASSIGNED', 'COLLECTION', 'RESOLVED'], default: 'REPORTED' },
}, { timestamps: true });

export default mongoose.model('Report', reportSchema);
