import crypto from 'node:crypto';
import Report from '../models/Report.js';

export async function createReport(payload) {
  const ticketId = `ECO-${crypto.randomInt(1000, 9999)}`;
  return Report.create({ ...payload, ticketId });
}
