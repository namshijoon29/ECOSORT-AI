import mongoose from 'mongoose';

const messageSchema = new mongoose.Schema({
  role: { type: String, enum: ['user', 'assistant'], required: true },
  content: { type: String, required: true },
}, { _id: false });

const chatSessionSchema = new mongoose.Schema({
  user: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
  status: { type: String, enum: ['AWAITING_CREDENTIALS', 'ACTIVE'], default: 'AWAITING_CREDENTIALS' },
  messages: { type: [messageSchema], default: [] },
}, { timestamps: true });

export default mongoose.model('ChatSession', chatSessionSchema);
