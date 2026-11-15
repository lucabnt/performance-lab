import {test} from 'node:test';
import assert from 'node:assert/strict';
import {chartTablePage, chartSummary} from '../src/chartAccessibility.ts';
test('accessible chart preserves missing values, zero and independent trace coordinates', () => {
  const data = [
    {name: 'W', x: [0, 1, 2], y: [0, null, 250]},
    {name: 'bpm', x: [0.5, 1.5], y: [120, 140]}
  ];
  assert.deepEqual(chartSummary(data), [
    {name: 'W', count: 2, min: 0, max: 250},
    {name: 'bpm', count: 2, min: 120, max: 140}
  ]);
  assert.deepEqual(chartTablePage(data, 1, 2).rows, [
    {name: 'W', x: 2, y: 250},
    {name: 'bpm', x: 0.5, y: 120}
  ]);
  assert.equal(chartTablePage(data, 0).rows[1].y, null);
});
test('large traces have bounded rows; out of range pages are clamped', () => {
  const data = [{y: Array.from({length: 100000}, (_, i) => i)}];
  assert.equal(chartTablePage(data, 0).rows.length, 30);
  const last = chartTablePage(data, 99999);
  assert.equal(last.rows.at(-1).y, 99999);
  assert.deepEqual(chartSummary([{y: [null, NaN, Infinity]}])[0], {name: '—', count: 0, min: null, max: null});
});
