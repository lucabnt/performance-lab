import test from 'node:test';
import assert from 'node:assert/strict';
import {loadArchiveSelection} from '../src/archiveSelection.ts';

test('remembered workspace and organization survive reload',async()=>{
 let current={workspace:'w1',organization:'club2'};
 const result=await loadArchiveSelection(async(path,_body,_method,workspace)=>{
  if(path==='workspaces'){assert.equal(workspace,'');return [{id:'w1'}]}
  assert.equal(workspace,'w1');return {organization:[{id:'club1'},{id:'club2'}]};
 },()=>current,s=>{current=s});
 assert.equal(result.organization,'club2');assert.equal(current.workspace,'w1');
});
test('stale ID falls back explicitly without sending it to state endpoint',async()=>{
 let current={workspace:'removed-demo',organization:'old'};
 const result=await loadArchiveSelection(async(path,_body,_method,workspace)=>{
  assert.equal(workspace,'');return path==='workspaces'?[]:{organization:[{id:'legacy'}]};
 },()=>current,s=>{current=s});
 assert.equal(result.missing,true);assert.deepEqual(current,{workspace:'',organization:'legacy'});
});
test('late response from a previous archive never replaces the new selection',async()=>{
 let current={workspace:'w1',organization:'a'},resolveState;
 const pending=loadArchiveSelection(async(path)=>path==='workspaces'?[{id:'w1'},{id:'w2'}]:await new Promise(r=>{resolveState=r}),()=>current,s=>{current=s});
 await new Promise(r=>setImmediate(r));
 current={workspace:'w2',organization:'b'};resolveState({organization:[{id:'a'}]});
 assert.equal(await pending,null);assert.deepEqual(current,{workspace:'w2',organization:'b'});
});

test('superseded refresh cannot persist a selection even for the same archive',async()=>{
 let written=false;
 const result=await loadArchiveSelection(async()=>[{id:'w1'}],()=>({workspace:'w1',organization:''}),()=>{written=true},()=>false);
 assert.equal(result,null);assert.equal(written,false);
});
