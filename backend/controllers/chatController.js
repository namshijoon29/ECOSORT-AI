import ChatSession from '../models/ChatSession.js';
import User from '../models/User.js';
import { answerChat, extractCredentials, temperature } from '../services/llmService.js';

const welcome = 'Welcome to EcoSort AI. I am EcoBot, your waste-sorting guide. Before we begin, please enter your username, user type (STUDENT or RESIDENT), and your registration number or employee/resident ID.';

export async function startChat(req, res) {
  const session = await ChatSession.create({ messages: [{ role: 'assistant', content: welcome }] });
  res.status(201).json({ success: true, sessionId: session._id, status: session.status, temperature, message: welcome });
}

export async function messageChat(req, res) {
  const { sessionId, message } = req.body;
  if (!sessionId || !message?.trim()) return res.status(400).json({ success: false, message: 'sessionId and message are required.' });
  const session = await ChatSession.findById(sessionId);
  if (!session) return res.status(404).json({ success: false, message: 'Chat session not found.' });

  if (session.status === 'AWAITING_CREDENTIALS') {
    const credentials = await extractCredentials(message);
    if (!credentials.complete) {
      const reply = 'Thanks. I still need your username, STUDENT or RESIDENT user type, and registration number or employee/resident ID.';
      session.messages.push({ role: 'user', content: message }, { role: 'assistant', content: reply });
      await session.save();
      return res.json({ success: true, status: session.status, credentialsRequired: true, reply });
    }

    const identifier = credentials.identifier.trim();
    const query = credentials.userType === 'STUDENT' ? { registrationNumber: identifier } : { employeeId: identifier };
    const user = await User.findOneAndUpdate(query, {
      $set: { username: credentials.username.trim(), userType: credentials.userType },
      $setOnInsert: query,
    }, { new: true, upsert: true, runValidators: true });
    session.user = user._id;
    session.status = 'ACTIVE';
    const reply = `Nice to meet you, ${user.username}. Your EcoSort AI profile is ready. Ask me about waste sorting, your rewards, missions, or leaderboard.`;
    session.messages.push({ role: 'user', content: message }, { role: 'assistant', content: reply });
    await session.save();
    return res.json({ success: true, status: session.status, userId: user._id, credentialsRequired: false, reply });
  }

  const user = await User.findById(session.user);
  if (!user) return res.status(404).json({ success: false, message: 'Chat profile not found.' });
  const history = session.messages;
  const result = await answerChat({ user, history, message: message.trim() });
  session.messages.push({ role: 'user', content: message.trim() }, { role: 'assistant', content: result.reply });
  await session.save();
  res.json({ success: true, status: session.status, ...result, temperature });
}
