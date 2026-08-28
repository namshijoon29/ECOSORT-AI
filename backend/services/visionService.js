import OpenAI from 'openai';
import { wasteAnalysisSchema } from '../schemas/wasteAnalysisSchema.js';

const systemPrompt = `You are EcoSort AI's waste-vision classifier. Analyze the actual uploaded image, not a filename or a fixed demo value. Identify every visible waste object that can reasonably be classified. For each object return practical, conservative sorting guidance. Use one of these bin labels when appropriate: ORGANIC, RECYCLABLE, E-WASTE, SPECIAL. If the image is unclear, say so in the object name and use a low confidence. Never invent an object that is not visible.`;

export async function classifyWasteImage(file) {
  const apiKey = process.env.GROQ_API_KEY || process.env.AI_API_KEY;
  if (!apiKey) {
    const error = new Error('GROQ_API_KEY or AI_API_KEY is missing. Configure a vision model key before calling the scan endpoint.');
    error.statusCode = 503;
    error.publicMessage = 'Vision AI is not configured.';
    throw error;
  }

  const client = new OpenAI({ apiKey, baseURL: process.env.AI_BASE_URL || 'https://api.groq.com/openai/v1' });
  const imageData = `data:${file.mimetype};base64,${file.buffer.toString('base64')}`;
  const response = await client.chat.completions.create({
    model: process.env.VISION_MODEL || process.env.AI_MODEL || 'meta-llama/llama-4-scout-17b-16e-instruct',
    temperature: 1.5,
    response_format: { type: 'json_schema', json_schema: { name: 'ecosort_waste_result', strict: true, schema: wasteAnalysisSchema } },
    messages: [{ role: 'user', content: [
      { type: 'text', text: systemPrompt },
      { type: 'image_url', image_url: { url: imageData } },
    ] }],
  });

  const raw = response.choices?.[0]?.message?.content;
  if (!raw) throw Object.assign(new Error('Vision model returned no structured result.'), { statusCode: 502, publicMessage: 'Vision model returned no result.' });
  const result = JSON.parse(raw.replace(/^```json\s*|\s*```$/g, '').trim());
  return result.objects.map((item) => ({ ...item, confidence: Math.max(0, Math.min(1, Number(item.confidence))) }));
}
