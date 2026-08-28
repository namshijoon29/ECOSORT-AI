export const wasteAnalysisSchema = {
  type: 'object',
  additionalProperties: false,
  required: ['objects'],
  properties: {
    objects: {
      type: 'array',
      minItems: 1,
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['object', 'category', 'biodegradable', 'recyclable', 'hazardous', 'eWaste', 'recommendedBin', 'disposalAdvice', 'confidence'],
        properties: {
          object: { type: 'string' },
          category: { type: 'string' },
          biodegradable: { type: 'boolean' },
          recyclable: { type: 'boolean' },
          hazardous: { type: 'boolean' },
          eWaste: { type: 'boolean' },
          recommendedBin: { type: 'string', enum: ['ORGANIC', 'RECYCLABLE', 'E-WASTE', 'SPECIAL'] },
          disposalAdvice: { type: 'string' },
          confidence: { type: 'number', minimum: 0, maximum: 1 },
        },
      },
    },
  },
};
