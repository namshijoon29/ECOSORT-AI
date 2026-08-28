import User from '../models/User.js';

const studentFields = ['registrationNumber', 'collegeName', 'campus', 'hostel', 'block', 'roomNumber', 'department', 'year', 'avatar'];
const residentFields = ['employeeId', 'buildingName', 'flatNumber', 'tower', 'floor', 'area', 'city', 'avatar'];

function profileFor(type, body) {
  const fields = type === 'STUDENT' ? studentFields : residentFields;
  return Object.fromEntries(fields.filter((field) => body[field] !== undefined).map((field) => [field, body[field]]));
}

export async function register(req, res) {
  const userType = String(req.body.userType || '').toUpperCase();
  if (!['STUDENT', 'RESIDENT'].includes(userType)) return res.status(400).json({ success: false, message: 'userType must be STUDENT or RESIDENT.' });
  if (!req.body.username) return res.status(400).json({ success: false, message: 'username is required.' });
  if (userType === 'STUDENT' && !req.body.registrationNumber) return res.status(400).json({ success: false, message: 'registrationNumber is required for students.' });
  if (userType === 'RESIDENT' && !req.body.employeeId) return res.status(400).json({ success: false, message: 'employeeId or resident ID is required for residents.' });
  const user = await User.create({ userType, username: req.body.username, ...profileFor(userType, req.body) });
  res.status(201).json({ success: true, user });
}

export async function login(req, res) {
  const query = req.body.registrationNumber ? { registrationNumber: req.body.registrationNumber } : { _id: req.body.userId };
  const user = await User.findOne(query);
  if (!user) return res.status(404).json({ success: false, message: 'User not found.' });
  res.json({ success: true, user });
}

export async function getUser(req, res) {
  const user = await User.findById(req.params.id);
  if (!user) return res.status(404).json({ success: false, message: 'User not found.' });
  res.json({ success: true, user });
}

export async function updateUser(req, res) {
  const user = await User.findByIdAndUpdate(req.params.id, { $set: req.body }, { new: true, runValidators: true });
  if (!user) return res.status(404).json({ success: false, message: 'User not found.' });
  res.json({ success: true, user });
}
