import {language} from './i18n';
import {TimeInput} from './time';
type Row=Record<string,any>;
export function VO2Input({draft,change}:{draft:Row;change:(key:string,value:any)=>void}){
 const en=language==='en',rows:Row[]=draft.vo2||[];
 const update=(i:number,key:string,value:any)=>change('vo2',rows.map((r,j)=>i===j?{...r,[key]:value}:r));
 return <fieldset><legend>{en?'Measured oxygen uptake · VO₂':'Consumo di ossigeno misurato · VO₂'}</legend>
 <p>{en?'Import vo2_l_min in the trace CSV, import a separate gas CSV below, or enter timed measurements here. Choose one source. Peak uses the preset averaging window; isolated observations do not establish VO₂peak or VO₂max.':'Importa vo2_l_min nel CSV temporale, importa un CSV gas separato qui sotto oppure inserisci qui misure temporizzate. Scegli una sola fonte. Il picco usa la finestra media del preset; misure isolate non stabiliscono VO₂peak o VO₂max.'}</p>
 {rows.map((r,i)=><div className="form-grid" key={i}>
 <TimeInput label={en?'Time from trace':'Istante dal tracciato'} value={r.at_s} onChange={v=>update(i,'at_s',v)}/>
 <label>VO₂ · L/min<input type="number" min="0.001" step="any" value={r.vo2_l_min??''} onChange={e=>update(i,'vo2_l_min',e.target.value===''?null:Number(e.target.value))}/></label>
 <label>{en?'Source / note':'Fonte / nota'}<input value={r.note||''} onChange={e=>update(i,'note',e.target.value)}/></label>
 <button type="button" onClick={()=>change('vo2',rows.filter((_,j)=>j!==i))}>{en?'Remove measurement':'Rimuovi misura VO₂'}</button>
 </div>)}
 <button type="button" disabled={!!draft.gas_hash||rows.length>=20000} onClick={()=>change('vo2',[...rows,{at_s:rows.length?rows[rows.length-1].at_s+1:0,vo2_l_min:null,note:''}])}>{en?'Add VO₂ measurement':'Aggiungi misura VO₂'}</button>
 </fieldset>;
}
