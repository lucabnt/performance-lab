import test from 'node:test';
import assert from 'node:assert/strict';
import {previousScreen} from '../src/androidBackModel.ts';

test('back from a profile preserves the source section, filters stay owned by that view',()=>{
 const current={page:'athletes',selected:'synthetic-athlete',scroll:500};
 const history=[{page:'tests',selected:'',scroll:350}];
 assert.deepEqual(previousScreen(current,history),history[0]);
 assert.equal(history.length,1);
});
test('only the root athlete list permits native exit without a previous screen',()=>{
 assert.equal(previousScreen({page:'athletes',selected:'',scroll:0},[]),null);
 assert.deepEqual(previousScreen({page:'athletes',selected:'a',scroll:300},[]),{page:'athletes',selected:'',scroll:0});
 assert.deepEqual(previousScreen({page:'info',selected:'',scroll:0},[]),{page:'athletes',selected:'',scroll:0});
});
