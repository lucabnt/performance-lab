import test from 'node:test';
import assert from 'node:assert/strict';
import {historySeries,historyTraces,initialHistorySelection,historyCategories} from '../src/historyChartModel.ts';

const group=(label,protocol='p1',method='m1',value=100,n=2,source='n.d.')=>({label,protocol_id:protocol,method_key:method,method_label:'Metodo '+method,threshold_source:source,metrics:{map_w:{n,missing:value===null?1:0,median:value,mean:value}}});
const protocols=[{id:'p1',name:'Incrementale',version:'1'},{id:'p2',name:'Wingate',version:'1'}];

test('one trace per exact series, not per year; no empty protocols',()=>{
 const series=historySeries([group('2026'),group('2024'),group('2025'),group('2026','p2','m2',null,0)],protocols,'map_w');
 assert.equal(series.length,1);assert.equal(series[0].groups.length,3);
 const traces=historyTraces(series,'map_w','median','season');
 assert.equal(traces.length,1);assert.deepEqual(traces[0].x,['2024','2025','2026']);
 assert.equal(traces[0].mode,'lines+markers');
});
test('methods, protocols and threshold origins are never silently pooled',()=>{
 const series=historySeries([group('2026'),group('2026','p1','m2'),group('2026','p2'),group('2026','p1','m1',100,2,'dichiarato')],protocols,'map_w');
 assert.equal(series.length,4);assert.ok(series.every(s=>s.groups.length===1));
});
test('default shows only largest valid series and explicit selection is bounded',()=>{
 const series=historySeries([group('2026','p1','m1',100,9),...Array.from({length:5},(_,i)=>group('2026','p2','m'+i))],protocols,'map_w');
 assert.equal(initialHistorySelection(series,null).length,1);
 assert.equal(initialHistorySelection(series,null)[0],series[0].id);assert.equal(series[0].valid,9);
 assert.equal(initialHistorySelection(series,series.map(s=>s.id)).length,4);
 assert.deepEqual(initialHistorySelection(series,[]),[]);
 assert.deepEqual(initialHistorySelection(series,['outdated']),[]);
});
test('missing years interrupt curves and zeros remain valid',()=>{
 const series=historySeries([group('2024','p1','m1',0,1),group('2025','p1','m1',null,0),group('2026','p1','m1',120,1)],protocols,'map_w');
 const trace=historyTraces(series,'map_w','median','season')[0];
 assert.deepEqual(trace.y,[0,null,120]);assert.equal(trace.connectgaps,false);
 assert.equal(historyTraces(series,'map_w','mean','athlete')[0].mode,'markers');
});

test('global category order stays chronological when series have different years',()=>{
 const series=historySeries([group('2026','p1','m1',100,9),group('2024','p2','m2')],protocols,'map_w');
 assert.deepEqual(historyCategories(series),['2024','2026']);
 assert.equal(historyTraces(series,'map_w','median','season')[1].line.color,historyTraces([series[1]],'map_w','median','season')[0].line.color);
});
