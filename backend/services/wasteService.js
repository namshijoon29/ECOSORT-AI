const bins = new Set(['ORGANIC', 'RECYCLABLE', 'E-WASTE', 'SPECIAL']);

export function normalizeObjects(objects) {
  if (!Array.isArray(objects) || objects.length === 0) {
    throw Object.assign(new Error('Vision result did not contain waste objects.'), { statusCode: 502, publicMessage: 'No waste objects were detected.' });
  }
  return objects.map((item) => {
    const recommendedBin = String(item.recommendedBin || '').toUpperCase().split(/\s|\//)[0];
    return {
      object: String(item.object).trim(),
      category: String(item.category).trim(),
      biodegradable: Boolean(item.biodegradable),
      recyclable: Boolean(item.recyclable),
      hazardous: Boolean(item.hazardous),
      eWaste: Boolean(item.eWaste),
      recommendedBin: bins.has(recommendedBin) ? recommendedBin : 'SPECIAL',
      disposalAdvice: String(item.disposalAdvice).trim(),
      confidence: Number(item.confidence),
    };
  });
}

export function evaluateBin(objects, selectedBin) {
  const bin = String(selectedBin || '').toUpperCase();
  return bins.has(bin) && objects.every((item) => item.recommendedBin === bin);
}
