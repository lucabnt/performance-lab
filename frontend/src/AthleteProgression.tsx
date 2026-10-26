import {useEffect,useState} from 'react';
import {progressionSeries} from './athleteProgressionModel';
import {metricLabel as baseLabel} from './metrics';
type Row=Record<string,any>;
export function AthleteProgression({tests,protocols,metric,setMetric,metrics,label,Plot}:{tests:Row[];protocols:Row[];metric:string;setMetric:(m:string)=>void;metrics:string[];label:(m:string)=>string;Plot:any}){
 const [selection,setSelection]=useState<string[]|null>(null);
 useEffect(()=>setSelection(null),[metric]);
 const series=progressionSeries(tests,protocols,metric);
 const selected=selection??series.slice(0,1).map(s=>s.id),shown=series.filter(s=>selected.includes(s.id));
 return <section className="panel protocol"><div className="panel-head"><h2>{metric==='map_w'?'MAP storiche':'Progressione'}</h2><label>Metrica storico<select value={metric} onChange={e=>setMetric(e.target.value)}>{[...new Set(metrics)].map(m=><option key={m} value={m}>{label(m)}</option>)}</select></label></div>
  {!series.length?<p className="hint">Nessun valore disponibile per questa metrica. I risultati mancanti non valgono zero; W/kg con peso solo stimato sono esclusi.</p>:<>
   <details><summary>Serie della progressione ({shown.length}/4)</summary><p>Protocolli, metodi e origini della soglia restano distinti. Scegli fino a quattro serie da affiancare.</p><div className="history-series">{series.map(s=><label className="history-series-option" key={s.id}><input type="checkbox" checked={selected.includes(s.id)} disabled={selected.length>=4&&!selected.includes(s.id)} onChange={e=>setSelection(e.target.checked?[...selected,s.id]:selected.filter(id=>id!==s.id))}/><span><strong>{s.code} · {s.title}</strong><small>{s.method} · origine soglia: {baseLabel(s.source)} · {s.valid} valori validi</small></span></label>)}</div></details>
   {shown.length?<Plot data={shown.map(s=>({x:s.tests.map((t:Row)=>t.date),y:s.tests.map((t:Row)=>t.analysis[metric]),text:s.tests.map((t:Row)=>t.id),name:s.code+' · '+s.title,type:'scatter',mode:'lines+markers',connectgaps:false}))} layout={{height:360,yaxis:{title:{text:label(metric)}},xaxis:{title:{text:'Data della prova'},type:'date'},legend:{orientation:'h',y:-.25},margin:{l:65,r:20,t:25,b:100}}}/>:<p>Seleziona almeno una serie.</p>}
   <div className="history-series-key">{shown.map(s=><p key={s.id}><strong>{s.code} · {s.title}</strong><small>{s.method} · origine soglia: {baseLabel(s.source)}</small></p>)}</div>
  </>}
 </section>;
}
