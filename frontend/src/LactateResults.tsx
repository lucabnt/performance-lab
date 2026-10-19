import {useState} from 'react';
import {numberText} from './metrics';
type Row=Record<string,any>;
const reasons:Row={no_crossing:'Livello non attraversato: nessuna estrapolazione',ambiguous_crossing:'Curva o attraversamento ambiguo',stage_hr_unavailable:'FC di fine step non disponibile o non sufficientemente coperta',weight_missing_or_estimated:'Peso assente o solo stimato'};
export function LactateResults({analysis:l,Plot}:{analysis:Row;Plot:any}){
 const [selected,setSelected]=useState<number|null>(null);
 const levels=Object.entries(l.results||{}).filter(([,r]:any)=>r.concentration_mmol_l!=null).map(([,r])=>r as Row);
 const estimated=levels.filter(r=>r.value!=null),points=l.points||[];
 const interpolable=points.length>=2&&points.every((p:Row,i:number)=>!i||(p.power_w>points[i-1].power_w&&p.mmol_l>=points[i-1].mmol_l));
 return <><h3>Lattato: potenza e FC ai livelli richiesti</h3>
  <p className="hint">Relazione fra carico (asse orizzontale, W) e lattato (asse verticale, mmol/L). Seleziona un punto o un livello per leggere potenza e FC nella tabella; il tracciato temporale mostra invece quando è avvenuto il prelievo.</p>
  <label>Livello evidenziato<select value={selected??''} onChange={e=>setSelected(e.target.value===''?null:Number(e.target.value))}><option value="">Tutti i livelli</option>{levels.map(r=><option key={r.concentration_mmol_l} value={r.concentration_mmol_l}>{numberText(r.concentration_mmol_l)} mmol/L</option>)}</select></label>
  <Plot onPoint={(p:Row)=>{const match=estimated.find(r=>Math.abs(r.value-p?.x)<.01&&Math.abs(r.concentration_mmol_l-p?.y)<.01);if(match)setSelected(match.concentration_mmol_l)}} data={[
   {x:points.map((r:Row)=>r.power_w),y:points.map((r:Row)=>r.mmol_l),type:'scatter',mode:'markers',name:'Prelievi associati al carico',marker:{size:9}},
   ...(interpolable?[{x:points.map((r:Row)=>r.power_w),y:points.map((r:Row)=>r.mmol_l),type:'scatter',mode:'lines',name:'Interpolazione lineare',line:{dash:'dash',color:'#1a62b7'}}]:[]),
   {x:estimated.map(r=>r.value),y:estimated.map(r=>r.concentration_mmol_l),text:estimated.map(r=>numberText(r.hr_bpm)+' bpm · '+numberText(r.wkg)+' W/kg'),type:'scatter',mode:'markers',name:'Valori stimati ai livelli richiesti',marker:{symbol:'diamond',size:10,color:'#b44d78'}},
   ...(l.curve?.length?[{x:l.curve.map((r:Row)=>r.power_w),y:l.curve.map((r:Row)=>r.mmol_l),type:'scatter',mode:'lines',visible:'legendonly',name:'Fit cubico per Dmax',line:{dash:'dot'}}]:[]),
  ]} layout={{xaxis:{title:{text:'Carico associato · W'}},yaxis:{title:{text:'Lattato · mmol/L'}},shapes:estimated.filter(r=>selected==null||selected===r.concentration_mmol_l).flatMap(r=>[{type:'line',xref:'x',yref:'paper',x0:r.value,x1:r.value,y0:0,y1:1,line:{color:'#b44d78',dash:'dot',width:1}},{type:'line',xref:'paper',x0:0,x1:1,y0:r.concentration_mmol_l,y1:r.concentration_mmol_l,line:{color:'#b44d7833',dash:'dot',width:1}}])}}/>
  <div className="table-scroll"><table><thead><tr><th>Livello · mmol/L</th><th>Potenza stimata · W</th><th>W/kg stimati</th><th>FC stimata · bpm</th><th>Disponibilità</th></tr></thead><tbody>{levels.map(r=><tr key={r.concentration_mmol_l} className={selected===r.concentration_mmol_l?'selected-row':''} aria-selected={selected===r.concentration_mmol_l}><td>{numberText(r.concentration_mmol_l)}</td><td>{numberText(r.value)}</td><td>{numberText(r.wkg)}</td><td>{numberText(r.hr_bpm)}</td><td>{r.reason?reasons[r.reason]||r.reason:[r.hr_reason&&reasons[r.hr_reason],r.weight_reason&&reasons[r.weight_reason]].filter(Boolean).join(' · ')||(l.method_snapshot?'Stime da interpolazione':'Revisione precedente: FC e W/kg non calcolati')}</td></tr>)}</tbody></table></div>
  {l.method_snapshot&&<p className="muted">FC: media degli ultimi {l.method_snapshot.hr_window_s} s degli step completi a carico costante, copertura minima {numberText(l.method_snapshot.hr_coverage*100)}%. Il battito al momento del prelievo non viene usato come FC dello step. Potenza associata al target del protocollo o a un carico dichiarato.</p>}
  <p className="hint">Stime tra prelievi che racchiudono il livello, senza estrapolazione. Le concentrazioni fisse non identificano automaticamente LT1, LT2, FTP o MLSS.</p>
 </>;
}
