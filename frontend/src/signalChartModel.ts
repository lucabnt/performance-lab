/** Pure chart model: stored observations only; summary values never become curves. */
export type SignalRow=Record<string,any>;
export const signalChannels=[
 {key:'power',label:'Potenza',unit:'W',color:'#1a62b7'},
 {key:'hr',label:'FC',unit:'bpm',color:'#bf523e'},
 {key:'cadence',label:'Cadenza',unit:'rpm',color:'#7952a3'},
 {key:'speed_kmh',label:'Velocità',unit:'km/h',color:'#248777'},
 {key:'temperature_c',label:'Temperatura',unit:'°C',color:'#ad7419'},
 {key:'altitude_m',label:'Quota',unit:'m',color:'#63734b'},
];
const finite=(v:unknown):v is number=>typeof v==='number'&&Number.isFinite(v);
export const hasRecordedTrace=(test:SignalRow)=>!!(test.has_trace||test.trace_hash||test.samples?.length);

/** A file reference or summary alone does not make a displayable chart. */
export const hasSignalChart=(test:SignalRow)=>
 (test.samples||[]).some((r:SignalRow)=>finite(r.t)&&(signalChannels.some(c=>finite(r[c.key]))||finite(r.lactate_mmol_l)))||
 (test.settings?.lactate||[]).some((r:SignalRow)=>finite(r.at_s)&&finite(r.mmol_l));

export function buildSignalChart(test:SignalRow,protocol?:SignalRow,selectedChannels?:string[]){
 const samples:SignalRow[]=(test.samples||[]).filter((r:SignalRow)=>finite(r.t));
 const availableChannels=signalChannels.filter(c=>samples.some((r:SignalRow)=>finite(r[c.key])));
 const channels=availableChannels.filter(c=>!selectedChannels||selectedChannels.includes(c.key));
 const timeline:SignalRow[]=[];
 const maxGap=test.settings?.preset?.max_gap_s??test.analysis?.protocol_snapshot?.max_gap_s??5;
 for(const row of samples){const previous=timeline.at(-1);if(previous&&row.t-previous.t>maxGap)timeline.push({t:(previous.t+row.t)/2});timeline.push(row)}
 const data:SignalRow[]=[],layout:SignalRow={height:440,hovermode:'x unified',margin:{l:65,r:65,t:65,b:55},legend:{orientation:'h',y:1.16},xaxis:{title:{text:'Tempo dal file · min'}},shapes:[]};
 const axisFor=(key:string)=>{const i=channels.findIndex(c=>c.key===key);return i<0?null:i===0?'y':'y'+(i+1)};
 channels.forEach((c,i)=>{
  const axis=i===0?'y':'y'+(i+1);
  layout[i===0?'yaxis':'yaxis'+(i+1)]={title:{text:c.label+' · '+c.unit,font:{color:c.color}},tickfont:{color:c.color},zeroline:false,...(i===0?{anchor:'x',gridcolor:'#e9edf3'}:{overlaying:'y',side:'right',anchor:'free',autoshift:true,showgrid:false})};
  data.push({x:timeline.map((r:SignalRow)=>r.t/60),y:timeline.map((r:SignalRow)=>finite(r[c.key])?r[c.key]:null),customdata:timeline.map((r:SignalRow)=>[r.t,`${Math.floor(r.t/60)}:${(r.t%60).toFixed(1).padStart(4,'0')}`]),hovertemplate:'%{customdata[1]} · %{customdata[0]:.3f} s<br>%{y} '+c.unit+'<extra>'+c.label+'</extra>',yaxis:axis,type:'scatter',mode:samples.length<50?'lines+markers':'lines',name:c.label+' · '+c.unit,line:{color:c.color,width:1.5},connectgaps:false});
 });
 const settings=test.settings||{},start=settings.offset_s??0;
 const end=finite(settings.end_s)?settings.end_s:finite(test.analysis?.protocol_snapshot?.duration_s)?start+test.analysis.protocol_snapshot.duration_s:null;
 for(const [time,color] of [[start,'#1a62b7'],[end,'#b44d78']] as const)if(time!=null)layout.shapes.push({type:'line',xref:'x',yref:'paper',x0:time/60,x1:time/60,y0:0,y1:1,line:{color,width:1,dash:'dash'}});
 if(end!=null&&end>start)layout.shapes.push({type:'rect',xref:'x',yref:'paper',x0:start/60,x1:end/60,y0:0,y1:1,fillcolor:'rgba(26,98,183,.06)',line:{width:0},layer:'below'});
 for(const r of settings.excluded_intervals||[])layout.shapes.push({type:'rect',xref:'x',yref:'paper',x0:r.start_s/60,x1:r.end_s/60,y0:0,y1:1,fillcolor:'rgba(190,70,40,.13)',line:{width:0},layer:'below'});
 if(axisFor('power')&&protocol?.definition?.segments?.length&&samples.length){
  const x:any[]=[],y:any[]=[];let shift=start,last=-1;
  const limit=Math.min(end??samples.at(-1)!.t,samples.at(-1)!.t);
  protocol.definition.segments.forEach((s:SignalRow,i:number)=>{
   const marker=(settings.alignment_markers||[]).find((m:SignalRow)=>m.number===i+1);
   if(marker)shift=marker.at_s-s.start_s;
   const a=shift+s.start_s,b=Math.min(limit,shift+s.end_s);
   if(a>=limit||b<=a)return;
   if(last>=0&&a>last){x.push(null);y.push(null)}
   x.push(a/60,b/60);y.push(s.start_w,s.start_w+(s.end_w-s.start_w)*(b-a)/(s.end_s-s.start_s));last=b;
  });
  data.unshift({x,y,type:'scatter',mode:'lines',name:'Target del protocollo · W',yaxis:axisFor('power'),line:{color:'#8a96a5',dash:'dot',width:1.5},connectgaps:false});
 }
 // Explicit prelievo time: never shift a measured marker to the fitted load.
 const lactate:{t:number;value:number;source:string}[]=(settings.lactate||[]).filter((r:SignalRow)=>finite(r.at_s)&&finite(r.mmol_l)).map((r:SignalRow)=>({t:r.at_s,value:r.mmol_l,source:'Prelievo'}));
 for(const r of samples)if(finite(r.lactate_mmol_l))lactate.push({t:r.t,value:r.lactate_mmol_l,source:'CSV'});
 if(lactate.length){
  const i=channels.length,axis=i===0?'y':'y'+(i+1);
  layout[i===0?'yaxis':'yaxis'+(i+1)]={title:{text:'Lattato · mmol/L',font:{color:'#b44d78'}},tickfont:{color:'#b44d78'},zeroline:false,...(i===0?{anchor:'x'}:{overlaying:'y',side:'right',anchor:'free',autoshift:true,showgrid:false})};
  data.push({x:lactate.map(r=>r.t/60),y:lactate.map(r=>r.value),text:lactate.map(r=>r.source),customdata:lactate.map(r=>r.t),hovertemplate:'%{customdata:.3f} s dal file<br>%{y} mmol/L<extra>Prelievo</extra>',yaxis:axis,type:'scatter',mode:'markers',name:'Lattato · mmol/L',marker:{size:9,color:'#b44d78'},connectgaps:false});
 }
 return {samples,availableChannels,channels,data,layout,lactate:lactate.sort((a:SignalRow,b:SignalRow)=>a.t-b.t)};
}
