import React,{useEffect,useRef,useState} from 'react';
import {tr} from './i18n';
type Row=Record<string,any>;
type Action='preview'|'pdf'|'md';
export function ArchiveReports({org,state,api,run,download}:{org:string,state:Row,api:any,run:any,download:any}){
 const [group,setGroup]=useState(''),[season,setSeason]=useState(''),[athlete,setAthlete]=useState(''),[preview,setPreview]=useState<Row|null>(null),[activity,setActivity]=useState<Action|null>(null);
 const inFlight=useRef(false);
 useEffect(()=>{setGroup('');setSeason('');setAthlete('');setPreview(null)},[org]);
 const working=activity!==null,query=new URLSearchParams({group,season,athlete}).toString();
 const perform=(action:Action)=>{
  if(inFlight.current)return;
  inFlight.current=true;setActivity(action);
  run(async()=>{try{
   if(action==='preview')setPreview(await api(`archive/${org}/report-data?${query}`));
   else await download(`archive/${org}/report/${action}?${query}`,'fuorigiri-archivio.'+(action==='pdf'?'pdf':'zip'));
  }finally{inFlight.current=false;setActivity(null)}});
 };
 const labels:Record<Action,string>={preview:'Anteprima contenuto',pdf:'Esporta PDF',md:'Esporta Markdown + grafici'};
 const ongoing:Record<Action,string>={preview:'Preparazione anteprima…',pdf:'Generazione PDF…',md:'Generazione Markdown e grafici…'};
 return <section className="panel protocol" aria-busy={working}>
  <h2>{tr('Report completo dell’archivio')}</h2><p>{tr('Società completa oppure una sua vista: gruppo, gruppo per anno/stagione, atleta con storico. Stessi criteri e sezioni; dati individuali riportati una sola volta.')}</p>
  <div className="form-grid"><label>{tr('Gruppo')}<select disabled={working} value={group} onChange={e=>{setGroup(e.target.value);setPreview(null)}}><option value="">{tr('Intera società')}</option>{state.group.filter((g:Row)=>g.organization_id===org).map((g:Row)=><option key={g.id} value={g.id}>{g.name} {g.season}</option>)}</select></label><label>{tr('Anno / stagione')}<input disabled={working} value={season} onChange={e=>{setSeason(e.target.value);setPreview(null)}} placeholder={tr('Tutti')}/></label><label>{tr('Atleta')}<select disabled={working} value={athlete} onChange={e=>{setAthlete(e.target.value);setPreview(null)}}><option value="">{tr('Tutti')}</option>{state.athlete.filter((a:Row)=>a.organization_id===org&&a.status!=='deleted').map((a:Row)=><option key={a.id} value={a.id}>{a.surname} {a.name}</option>)}</select></label></div>
  <div className="actions">{(['preview','pdf','md'] as Action[]).map(action=><button key={action} disabled={working} onClick={()=>perform(action)}>{activity===action&&<span className="suite-spinner" aria-hidden="true"/>}{tr(activity===action?ongoing[action]:labels[action])}</button>)}</div>
  {working&&<p role="status" aria-live="polite">{tr(activity==='preview'?'Preparazione del contenuto in corso.':'Elaborazione in corso. Il download partirà al termine: non serve premere nuovamente.')}</p>}
  {preview&&<p>{preview.counts.athletes} {tr('atleti')} · {preview.counts.tests} {tr('test')} · {preview.counts.measurements} {tr('misure')} · {preview.sections.length} {tr('viste aggregate. L’export include le schede individuali e il catalogo dei protocolli usati.')}</p>}
 </section>;
}
