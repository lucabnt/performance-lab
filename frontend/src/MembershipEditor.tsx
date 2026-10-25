import {seasonPeriod} from './groupSeasonModel';
import React,{useState} from 'react';
import {DataTable,FormActions} from '@cycling-suite/ui';
import {tr} from './i18n';
type Row=Record<string,any>;
const today=()=>new Date().toLocaleDateString('en-CA');
export function MembershipEditor({athletes,groups,memberships,athleteId,groupId,api,run,done,busy=false}:{athletes:Row[],groups:Row[],memberships:Row[],athleteId?:string,groupId?:string,api:any,run:any,done:any,busy?:boolean}){
 const initialGroup=groupId||groups[0]?.id||'';
 const initialPeriod=seasonPeriod(groups.find(g=>g.id===initialGroup)?.season,today());
 const [group,setGroup]=useState(initialGroup),[start,setStart]=useState(initialPeriod.start),[end,setEnd]=useState(initialPeriod.end),[year,setYear]=useState(''),[query,setQuery]=useState(''),[picked,setPicked]=useState<string[]>([]);
 const active=athletes.filter(a=>(a.status||'active')==='active').sort((a,b)=>`${a.surname} ${a.name}`.localeCompare(`${b.surname} ${b.name}`));
 const assigned=(id:string)=>memberships.some(m=>m.athlete_id===id&&m.group_id===group&&m.status!=='deleted'&&m.start<=(end||'9999-12-31')&&(!m.end||m.end>=start));
 const available=active.filter(a=>!assigned(a.id));
 const shown=active.filter(a=>`${a.surname} ${a.name}`.toLocaleLowerCase().includes(query.trim().toLocaleLowerCase()));
 const eligible=shown.filter(a=>!assigned(a.id));
 const selected=athleteId?(available.some(a=>a.id===athleteId)?[athleteId]:[]):picked.filter(id=>available.some(a=>a.id===id));
 const all=eligible.length>0&&eligible.every(a=>selected.includes(a.id));
 const toggle=(id:string)=>setPicked(ids=>ids.includes(id)?ids.filter(x=>x!==id):[...ids,id]);
 const label=(g:Row)=>[g.name,g.season].filter(Boolean).join(' · ');
 return <form onSubmit={e=>{e.preventDefault();run(async()=>{const result=await api('memberships/batch',{group_id:group,athlete_ids:selected,start,end:end||null,category_year:year?Number(year):null});await done(result)})}}>
  <h2>{tr(athleteId?'Aggiungi a un gruppo':'Aggiungi atleti')}</h2>
  {athleteId&&<p>{athletes.find(a=>a.id===athleteId)?.surname} {athletes.find(a=>a.id===athleteId)?.name}</p>}
  <div className="form-grid">
   <label>{tr('Gruppo')}<select required disabled={!!groupId||busy} value={group} onChange={e=>{const id=e.target.value;setGroup(id);const period=seasonPeriod(groups.find(g=>g.id===id)?.season,today());setStart(period.start);setEnd(period.end)}}>{groups.map(g=><option key={g.id} value={g.id}>{label(g)}</option>)}</select></label>
   <label>{tr('Dal')}<input required type="date" value={start} onChange={e=>setStart(e.target.value)}/></label>
   <label>{tr('Al (facoltativo)')}<input type="date" min={start} value={end} onChange={e=>setEnd(e.target.value)}/></label>
   <label>{tr('Anno di categoria (1, 2…)')}<input type="number" min="1" max="20" value={year} onChange={e=>setYear(e.target.value)}/></label>
  </div>
  {athleteId?(assigned(athleteId)&&<p role="status">{tr('Atleta già assegnato al gruppo nel periodo indicato.')}</p>):<>
   <label>{tr('Cerca atleta')}<input type="search" value={query} onChange={e=>setQuery(e.target.value)}/></label>
   <p>{tr('Gli atleti già assegnati nel periodo indicato non sono selezionabili.')}</p>
   <label className="choice"><input type="checkbox" checked={all} disabled={!eligible.length||busy} onChange={()=>setPicked(ids=>all?ids.filter(id=>!eligible.some(a=>a.id===id)):[...new Set([...ids,...eligible.map(a=>a.id)])])}/>{tr('Seleziona tutti i risultati della ricerca')}</label>
   <p role="status">{tr('Atleti selezionati:')} {selected.length}</p>
   <DataTable rows={shown} columns={[{key:'select',label:tr('Seleziona'),render:a=><input type="checkbox" aria-label={`${tr('Seleziona')} ${a.surname} ${a.name}`} disabled={busy||assigned(a.id)} checked={selected.includes(a.id)} onChange={()=>toggle(a.id)}/>},{key:'surname',label:tr('Cognome')},{key:'name',label:tr('Nome')},{key:'birth_year',label:tr('Anno di nascita')},{key:'membership',label:tr('Appartenenza'),render:a=>assigned(a.id)?tr('Già assegnato nel periodo'):tr('Disponibile')}]}/>
   {!shown.length&&<p>{tr('Nessun atleta corrisponde alla ricerca.')}</p>}
  </>}
  {!groups.length&&<p>{tr('Crea prima un gruppo nella sezione Società e gruppi.')}</p>}
  <FormActions><button className="primary" disabled={busy||!group||!selected.length||!!end&&end<start}>{tr('Conferma assegnazione')}</button></FormActions>
 </form>;
}
