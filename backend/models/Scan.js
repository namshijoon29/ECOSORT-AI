import mongoose from 'mongoose';

const wasteObjectSchema = new mongoose.Schema({
  object: { type: String, required: true },
  category: { type: String, required: true },
  biodegradable: { type: Boolean, required: true },
  recyclable: { type: Boolean, required: true },
  hazardous: { type: Boolean, required: true },
  eWaste: { type: Boolean, required: true },
  recommendedBin: { type: String, required: true },
  disposalAdvice: { type: String, required: true },
  confidence: { type: Number, min: 0, max: 1, required: true },
}, { _id: false });

const scanSchema = new mongoose.Schema({
  user: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  imageName: String,
  imageMimeType: String,
  objects: { type: [wasteObjectSchema], required: true },
  selectedBin: String,
  correct: { type: Boolean, default: false },
  xpAwarded: { type: Number, default: 0 },
  creditsAwarded: { type: Number, default: 0 },
}, { timestamps: true });

export default mongoose.model('Scan', scanSchema);
