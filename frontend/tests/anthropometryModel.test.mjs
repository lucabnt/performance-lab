import test from 'node:test';
import assert from 'node:assert/strict';
import {bodyMassIndex, perinealHeightRatio} from '../src/anthropometryModel.ts';

test('perineal ratio uses only positive finite values in one observation', () => {
  assert.equal(perinealHeightRatio({height_cm: 160, perineal_height_cm: 80}), 50);
  for (const record of [
    {},
    {height_cm: 160},
    {perineal_height_cm: 80},
    {height_cm: 0, perineal_height_cm: 80},
    {height_cm: 160, perineal_height_cm: 0},
    {height_cm: 160, perineal_height_cm: 160},
    {height_cm: 160, perineal_height_cm: 170},
    {height_cm: Infinity, perineal_height_cm: 80},
    {height_cm: 160, perineal_height_cm: NaN},
    {height_cm: 160, perineal_height_cm: '80'}
  ])
    assert.equal(perinealHeightRatio(record), null);
  const records = [
    {date: '2026-01-01', height_cm: 160},
    {date: '2026-01-01', perineal_height_cm: 80}
  ];
  assert.deepEqual(records.map(perinealHeightRatio), [null, null]);
});

test('BMI converts centimetres to metres and keeps the unrounded result', () => {
  assert.equal(bodyMassIndex({weight_kg: 72, height_cm: 200}), 18);
  assert.ok(Math.abs(bodyMassIndex({weight_kg: 67.5, height_cm: 176}) - 21.791064049586777) < 1e-12);
});
test('partial, zero, nonnumeric and nonfinite measurements cannot produce BMI', () => {
  for (const record of [
    {},
    {weight_kg: 72},
    {height_cm: 180},
    {weight_kg: null, height_cm: 180},
    {weight_kg: 72, height_cm: 0},
    {weight_kg: 0, height_cm: 180},
    {weight_kg: -1, height_cm: 180},
    {weight_kg: 72, height_cm: -180},
    {weight_kg: NaN, height_cm: 180},
    {weight_kg: 72, height_cm: Infinity},
    {weight_kg: '72', height_cm: 180}
  ])
    assert.equal(bodyMassIndex(record), null);
  // Complementary records, even on the same day, are not merged.
  const records = [
    {date: '2026-01-01', weight_kg: 72},
    {date: '2026-01-01', height_cm: 180}
  ];
  assert.deepEqual(records.map(bodyMassIndex), [null, null]);
});
