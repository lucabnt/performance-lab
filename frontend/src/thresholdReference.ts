/** Read the saved input, never infer a coefficient from rounded watts. */
export function thresholdCoefficient(test: Record<string, any>): number | null {
  const settings = test.settings || {};
  const raw = Object.prototype.hasOwnProperty.call(settings, 'threshold_coefficient')
    ? settings.threshold_coefficient
    : test.historical_fields?.coeff_soglia;
  if (raw == null || String(raw).trim() === '') return null;
  const value = Number(String(raw).trim().replace(',', '.'));
  return Number.isFinite(value) && value > 0 && value <= 2 ? value : null;
}
