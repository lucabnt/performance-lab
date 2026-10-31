import test from 'node:test';
import assert from 'node:assert/strict';
import {buildSignalChart,hasRecordedTrace,hasSignalChart} from '../src/signalChartModel.ts';

test('overlaid channels use separate units and preserve zero/missing values',()=>{
 const m=buildSignalChart({samples:[{t:0,power:0,hr:90,cadence:0},{t:1,power:100,hr:null,cadence:85,speed_kmh:22}]});
 assert.deepEqual(m.channels.map(c=>c.key),['power','hr','cadence','speed_kmh']);
 assert.equal(new Set(m.data.map(d=>d.yaxis)).size,4);
 assert.deepEqual(m.data[0].y,[0,100]);assert.deepEqual(m.data[1].y,[90,null]);
 assert.ok(m.data.every(d=>d.visible!=='legendonly'));
 assert.equal(m.layout.yaxis2.overlaying,'y');assert.equal(m.layout.yaxis3.overlaying,'y');
 assert.equal(m.layout.yaxis2.autoshift,true);assert.equal(m.layout.yaxis3.domain,undefined);
});
test('manual summary values never generate a trace',()=>{
 const m=buildSignalChart({analysis:{peak_w:1000,fc_max_test_bpm:180},samples:[]});
 assert.equal(m.channels.length,0);assert.equal(hasRecordedTrace({analysis:{peak_w:1000}}),false);
 assert.equal(hasRecordedTrace({has_trace:true}),true);
});
test('measured lactate stays at collection time independently from load delay',()=>{
 const m=buildSignalChart({samples:[{t:10,lactate_mmol_l:2.1}],settings:{lactate:[{at_s:90,mmol_l:4.2,delay_s:30}]}});
 assert.deepEqual(m.lactate.map(r=>[r.t,r.value]),[[10,2.1],[90,4.2]]);
 assert.equal(m.channels.length,0);
});
test('long gaps interrupt curves, without invented observations',()=>{
 const m=buildSignalChart({samples:[{t:0,power:100},{t:20,power:200}]});
 assert.equal(m.samples.length,2);assert.deepEqual(m.data[0].y,[100,null,200]);
});
test('target uses the power axis, alignment and end of effort',()=>{
 const m=buildSignalChart({samples:[{t:0,power:100},{t:1,power:100},{t:2,power:100}],settings:{offset_s:1,end_s:2}}, {definition:{segments:[{start_s:0,end_s:10,start_w:80,end_w:80}]}});
 assert.deepEqual(m.data[0].x,[1/60,2/60]);assert.equal(m.data[0].yaxis,'y');
});

test('optional channels can be selected without changing the original observations',()=>{
 const original={samples:[{t:0,power:100,cadence:90,temperature_c:20},{t:1,power:110,cadence:91,temperature_c:21}]};
 const m=buildSignalChart(original,undefined,['power','cadence']);
 assert.deepEqual(m.channels.map(c=>c.key),['power','cadence']);assert.equal(m.availableChannels.length,3);
 assert.equal(original.samples[0].temperature_c,20);
});
test('lactate markers overlay the same timeline on their own unit axis',()=>{
 const m=buildSignalChart({samples:[{t:0,power:100,hr:90,cadence:80}],settings:{lactate:[{at_s:60,mmol_l:2.1}]}});
 assert.equal(m.data.at(-1).yaxis,'y4');assert.equal(m.layout.yaxis4.overlaying,'y');
 assert.equal(m.data.at(-1).mode,'markers');assert.deepEqual(m.data.at(-1).x,[1]);
});


test('chart placement requires real plottable observations, including zero and lactate-only data',()=>{
 for(const row of [{analysis:{map_w:180,fc_max_test_bpm:190}}, {has_trace:true,trace_hash:'missing'}, {samples:[{t:0,power:null}]}, {samples:[{t:NaN,power:100}]}]) {
  assert.equal(hasSignalChart(row),false);
  assert.equal(buildSignalChart(row).data.length,0);
 }
 for(const row of [{samples:[{t:0,power:0}]}, {samples:[{t:3,temperature_c:20}]}, {samples:[{t:0,lactate_mmol_l:1}]}, {settings:{lactate:[{at_s:0,mmol_l:0}]}}]) {
  assert.equal(hasSignalChart(row),true);
  assert.ok(buildSignalChart(row).data.length>0);
 }
});


test('VO2 shares the timeline with an independent axis, preserving manual times and gaps',()=>{
 const testRow={samples:[{t:0,power:100},{t:1,power:110}],settings:{vo2:[{at_s:0,vo2_l_min:2},{at_s:60,vo2_l_min:3}]}};
 const m=buildSignalChart(testRow);
 assert.equal(hasSignalChart(testRow),true);
 const gas=m.data.find(r=>r.name==='VO₂ · L/min');
 assert.equal(gas.yaxis,'y2');assert.deepEqual(gas.y,[2,null,3]);assert.equal(gas.mode,'markers');
 const shifted=buildSignalChart({analysis:{gas:{samples:[{t:20,vo2:3},{t:21,vo2:4}]}}});
 assert.deepEqual(shifted.data[0].x,[20/60,21/60]);
 assert.equal(hasSignalChart({analysis:{vo2peak_l_min:3}}),false);
});
