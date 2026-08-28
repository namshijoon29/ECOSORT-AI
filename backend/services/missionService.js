import Mission from '../models/Mission.js';

export async function listMissions(userType) {
  const type = String(userType || '').toUpperCase();
  return Mission.find({ active: true, $or: [{ userType: 'BOTH' }, ...(type ? [{ userType: type }] : [])] }).sort({ createdAt: -1 }).lean();
}
