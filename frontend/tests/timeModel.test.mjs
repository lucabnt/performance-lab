import test from 'node:test';
import assert from 'node:assert/strict';
import {clock,parseClock} from '../src/timeModel.ts';
test('clock and seconds agree without confusing decimal minutes',()=>{
 assert.equal(parseClock('23:45'),1425);assert.equal(clock(1425),'23:45');
 assert.equal(parseClock('23:60'),null);assert.equal(parseClock('23.45'),null);
 assert.equal(parseClock('0:00'),0);assert.equal(parseClock('1:01,125'),61.125);
 assert.equal(clock(61.125),'1:01.125');assert.equal(parseClock('-1:00'),null);
 assert.equal(clock(59.9999),'1:00');
});
