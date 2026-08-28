import OpenAI from 'openai';
import { chatReplySchema } from '../schemas/chatReplySchema.js';
import { credentialSchema } from '../schemas/credentialSchema.js';

const temperature = 1.5;

function getClient() {
  const apiKey = process.env.GROQ_API_KEY || process.env.AI_API_KEY;
  if (!apiKey) {
    const error = new Error('GROQ_API_KEY or AI_API_KEY is missing.');
    error.statusCode = 503;
    error.publicMessage = 'EcoBot AI is not configured.';
    throw error;
  }
  return new OpenAI({ apiKey, baseURL: process.env.AI_BASE_URL || 'https://api.groq.com/openai/v1' });
}

function modelFor(kind) {
  if (kind === 'vision') return process.env.VISION_MODEL || process.env.AI_MODEL || 'meta-llama/llama-4-scout-17b-16e-instruct';
  return process.env.CHAT_MODEL || process.env.AI_MODEL || 'llama-3.3-70b-versatile';
}

function parseStructured(response) {
  const text = response.choices?.[0]?.message?.content;
  if (!text) throw Object.assign(new Error('The language model returned an empty response.'), { statusCode: 502, publicMessage: 'EcoBot did not return a response.' });
  return JSON.parse(text.replace(/^```json\s*|\s*```$/g, '').trim());
}

export async function extractCredentials(message) {
  const response = await getClient().chat.completions.create({
    model: modelFor('chat'),
    temperature,
    response_format: { type: 'json_schema', json_schema: { name: 'ecosort_credentials', strict: true, schema: credentialSchema } },
    messages: [
      { role: 'system', content: 'Extract EcoSort AI credentials from the user message. userType must be STUDENT or RESIDENT. For STUDENT, identifier is registrationNumber. For RESIDENT, identifier is employeeId or resident ID. Never invent missing values. Set complete false when username, userType, or identifier is missing.' },
      { role: 'user', content: message },
    ],
  });
  return parseStructured(response);
}

export async function answerChat({ user, history, message }) {
  const profile = JSON.stringify({ username: user.username, userType: user.userType, credits: user.credits, xp: user.xp, level: user.level, streak: user.streak, scans: user.scanCount });
  const response = await getClient().chat.completions.create({
    model: modelFor('chat'),
    temperature,
    response_format: { type: 'json_schema', json_schema: { name: 'ecosort_chat_reply', strict: true, schema: chatReplySchema } },
    messages: [
      { role: 'system', content: `You are EcoBot, the friendly assistant for EcoSort AI. Give the most relevant answer to the user's question using the profile context. Be concise, practical, and never claim that a payment, pickup, or real-world action happened unless the API confirms it. EcoSort AI identifies waste from images, explains segregation, and rewards correct sorting. Temperature is set to ${temperature}. Profile: ${profile}` },
      ...history.slice(-10).map((item) => ({ role: item.role, content: item.content })),
      { role: 'user', content: message },
    ],
  });
  return parseStructured(response);
}

export { temperature };
