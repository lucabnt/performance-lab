import test from 'node:test';
import assert from 'node:assert/strict';
import {progressionSeries} from '../src/athleteProgressionModel.ts';
const t = (id, date, source, value, weight = 'misurato') => ({
  id,
  date,
  protocol_id: 'p',
  settings: {weight_source: weight},
  analysis: {comparison_key: 'same-method', threshold_source: source, map_w: value, map_wkg: value}
});
test('profile progressions keep threshold sources separate and exclude empty series', () => {
  const series = progressionSeries(
    [t('a', '2026-01-01', null, 100), t('b', '2026-02-01', 'dichiarato', 110), t('c', '2026-03-01', null, null)],
    [],
    'map_w'
  );
  assert.equal(series.length, 2);
  assert.ok(series.every(s => s.valid === 1));
  assert.equal(series.find(s => s.source === 'n.d.').tests[1].analysis.map_w, null);
});
test('relative progressions exclude estimated weight and keep zero observations', () => {
  const series = progressionSeries(
    [t('b', '2026-02-01', null, 120, 'stimato'), t('a', '2026-01-01', null, 0)],
    [],
    'map_wkg'
  );
  assert.equal(series.length, 1);
  assert.equal(series[0].tests[0].analysis.map_wkg, 0);
});
