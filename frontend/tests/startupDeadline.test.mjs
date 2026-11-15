import test from 'node:test';
import assert from 'node:assert/strict';
import {withDeadline} from '../src/startupDeadline.ts';

test('startup continues or fails explicitly instead of waiting forever for the bridge', async () => {
  assert.equal(await withDeadline(Promise.resolve('en'), 100, 'timeout'), 'en');
  await assert.rejects(withDeadline(new Promise(() => {}), 10, 'bridge unavailable'), /bridge unavailable/);
  await assert.rejects(withDeadline(Promise.reject(new Error('disk error')), 100, 'timeout'), /disk error/);
});
