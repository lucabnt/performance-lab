import test from 'node:test';
import assert from 'node:assert/strict';
import {groupSeasons,matchesGroupMembership,seasonPeriod,groupFilterLabel} from '../src/groupSeasonModel.ts';
const groups=[{id:'allievi',name:'Allievi',season:'2026'},{id:'2027',name:'Allievi',season:'2027',parent_id:'allievi'}];
const today='2026-10-25';
test('legacy root season and future season are siblings without changing IDs or data',()=>{
 const original=structuredClone(groups);
 assert.deepEqual(groupSeasons(groups[0],groups,[]).map(g=>g.id),['allievi','2027']);
 assert.deepEqual(groups,original);
 assert.equal(groupFilterLabel('allievi',groups),'Allievi');
 assert.equal(groupFilterLabel('season:allievi',groups),'Allievi · 2026');
});
test('season roster includes future, expired and boundary memberships only in its own group',()=>{
 const match=m=>matchesGroupMembership(m,'season:2027',groups,today);
 assert.equal(match({group_id:'2027',start:'2027-03-01',end:'2027-06-01'}),true);
 assert.equal(match({group_id:'2027',start:'2026-01-01',end:'2027-01-01'}),true);
 assert.equal(match({group_id:'2027',start:'2027-12-31'}),true);
 assert.equal(match({group_id:'2027',start:'2028-01-01'}),false);
 assert.equal(match({group_id:'2027',start:'2026-01-01',end:'2026-12-31'}),false);
 assert.equal(match({group_id:'allievi',start:'2027-01-01'}),false);
 assert.equal(match({group_id:'2027',start:'2027-01-01',status:'deleted'}),false);
});
test('category keeps current aggregation while legacy season excludes children',()=>{
 const current={group_id:'2027',start:'2026-01-01'};
 assert.equal(matchesGroupMembership(current,'allievi',groups,today),true);
 assert.equal(matchesGroupMembership(current,'season:allievi',groups,today),false);
 assert.equal(matchesGroupMembership({...current,start:'2027-01-01'},'allievi',groups,today),false);
});
test('season assignment defaults cover the selected year, with explicit fallback for nonannual legacy labels',()=>{
 assert.deepEqual(seasonPeriod('2027',today),{start:'2027-01-01',end:'2027-12-31'});
 assert.deepEqual(seasonPeriod('',today),{start:today,end:''});
 assert.deepEqual(seasonPeriod('2026/27',today),{start:today,end:''});
});
test('undated memberships remain visible separately from named seasons',()=>{
 const root={id:'root',name:'Esordienti'};
 const children=[root,{id:'child',parent_id:'root',season:'2027'}];
 assert.deepEqual(groupSeasons(root,children,[]).map(g=>g.id),['child']);
 assert.deepEqual(groupSeasons(root,children,[{group_id:'root'}]).map(g=>g.id),['root','child']);
 assert.deepEqual(groupSeasons(root,[root],[]),[]);
});
