export const credentialSchema = {
  type: 'object',
  additionalProperties: false,
  required: ['complete', 'username', 'userType', 'identifier'],
  properties: {
    complete: { type: 'boolean' },
    username: { type: 'string' },
    userType: { type: 'string', enum: ['STUDENT', 'RESIDENT'] },
    identifier: { type: 'string' },
    registrationNumber: { type: ['string', 'null'] },
    employeeId: { type: ['string', 'null'] },
  },
};
