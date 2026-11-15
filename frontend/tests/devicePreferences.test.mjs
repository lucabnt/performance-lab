import test from 'node:test';
import assert from 'node:assert/strict';
import {rememberedLanguage, syncTime} from '../src/devicePreferences.ts';

test('device language overrides a fresh origin cache, with validated fallback', async () => {
  assert.equal(await rememberedLanguage(async () => ({language: 'en'}), 'it'), 'en');
  assert.equal(await rememberedLanguage(async () => ({language: 'it'}), 'en'), 'it');
  assert.equal(await rememberedLanguage(async () => ({language: null}), 'en'), 'en');
  assert.equal(await rememberedLanguage(async () => ({}), 'bad'), 'it');
});
test('sync times apply Rome DST, UTC and do not invent an offset for legacy dates', () => {
  assert.match(syncTime('2026-10-25T16:23:39+00:00', 'Europe/Rome'), /17:23:39/);
  assert.match(syncTime('2026-07-25T16:23:39Z', 'Europe/Rome'), /18:23:39/);
  assert.match(syncTime('2026-10-25T16:23:39Z', 'UTC'), /16:23:39/);
  assert.match(syncTime('2026-10-25T16:23:39', 'Europe/Rome'), /fuso non indicato/);
});
