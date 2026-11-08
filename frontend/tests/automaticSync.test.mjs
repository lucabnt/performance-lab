import test from 'node:test';
import assert from 'node:assert/strict';
import {AutomaticSync,isArchiveWrite} from '../src/automaticSync.ts';
test('sync on open, debounce writes, receive periodically, never overlap',()=>{
 const s=new AutomaticSync(0);assert.ok(s.due(0));s.started();assert.ok(!s.due(999999));s.finished(1000,true);
 assert.ok(!s.due(300999));assert.ok(s.due(301000));
 s.changed(2000);s.changed(4000);assert.ok(!s.due(13999));assert.ok(s.due(14000));
 s.started();s.changed(15000);s.finished(17000,true);assert.ok(!s.due(24999));assert.ok(s.due(25000));
});
test('failure retry grows, new writes do not bypass backoff, success resets it',()=>{
 const s=new AutomaticSync(0);s.started();s.finished(0,false);assert.equal(s.retryAt,30000);
 s.changed(1);assert.ok(!s.due(10001));assert.ok(s.due(30000));s.started();s.finished(30000,false);assert.equal(s.retryAt,90000);
 for(let n=0;n<12;n++){s.started();s.finished(s.retryAt,false)}
 const at=s.retryAt;s.started();s.finished(at,false);assert.equal(s.retryAt-at,1800000);
 s.started();s.finished(s.retryAt,true);assert.equal(s.failures,0);assert.equal(s.retryAt,0);
});
test('only archive writes trigger automatic exchange, not polling or previews',()=>{
 for(const p of ['athletes/a?base=r','organizations/o/integrations','memberships/batch','import/commit','tests','records/a/status','conflicts/c/resolve','workspace/revoke/member'])assert.ok(isArchiveWrite(p,'POST'),p);
 for(const p of ['sync/start','sync/automatic','device/preferences','workspaces/last-selection','tests/preview','anaerobic/preview','import/preview'])assert.ok(!isArchiveWrite(p,'POST'),p);
 assert.ok(!isArchiveWrite('athletes','GET'));
});
