import {useEffect,useRef,useState} from 'react';
import {tr} from './i18n';
import {AutomaticSync} from './automaticSync';
type Row=Record<string,any>;
export function useSyncJob(api:any,workspace:string,onFinished:()=>void){
 const [job,setJob]=useState<Row>({status:'idle'}),[starting,setStarting]=useState(false),[error,setError]=useState('');
 const generation=useRef(0),startingRef=useRef(false),finished=useRef(onFinished),observed=useRef('');
 const [automatic,setAutomatic]=useState<Row>({enabled:false,configured:false});
 const auto=useRef<{workspace:string;clock:AutomaticSync;prefs:Row}|null>(null);
 const wake=useRef<(()=>void)|null>(null);
 finished.current=onFinished;
 const accept=(next:Row)=>{setJob(next);setError('');if(next.status==='running')observed.current=next.id;else if(observed.current===next.id){observed.current='';const current=auto.current;if(current?.clock.busy)current.clock.finished(Date.now(),next.status==='completed'&&!next.result?.errors?.length&&!next.result?.pending);finished.current()}};
 useEffect(()=>{const current=++generation.current;let stopped=false,timer:ReturnType<typeof setTimeout>;
  setJob({status:'idle'});setError('');observed.current='';
  if(!workspace)return;
  const poll=async()=>{try{const next=await api('sync/job',undefined,'GET',workspace);if(stopped||current!==generation.current)return;
    if(!observed.current||next.id===observed.current){if(next.status==='running'&&auto.current&&!auto.current.clock.busy)auto.current.clock.started();accept(next);}
    clearTimeout(timer);timer=setTimeout(poll,next.status==='running'||observed.current?1200:6000);
   }catch(e){if(stopped)return;if(observed.current)setError((e as Error).message);timer=setTimeout(poll,observed.current?2500:10000)}};
  wake.current=()=>{clearTimeout(timer);timer=setTimeout(poll,50)};
  poll();return()=>{stopped=true;clearTimeout(timer);wake.current=null};
 },[workspace]);
 const start=async(verify_all=false)=>{
  if(startingRef.current)return;
  startingRef.current=true;setStarting(true);const current=generation.current;
  auto.current?.clock.started();
  try{const next=await api('sync/start',{verify_all},'POST',workspace);if(current===generation.current){observed.current=next.id;accept(next);wake.current?.()}}catch(e){if(current===generation.current)auto.current?.clock.finished(Date.now(),false);throw e}finally{startingRef.current=false;setStarting(false)}
 };
 const reloadAutomatic=async()=>{
  const selected=workspace,current=auto.current;
  const prefs=await api('sync/automatic',undefined,'GET',selected);
  if(current&&auto.current===current&&current.workspace===selected){auto.current.prefs=prefs;setAutomatic(prefs);}
 };
 useEffect(()=>{
  if(!workspace){auto.current=null;setAutomatic({enabled:false,configured:false});return;}
  const current={workspace,clock:new AutomaticSync(Date.now()),prefs:{enabled:false,configured:false}};
  auto.current=current;setAutomatic(current.prefs);let stopped=false;
  let retry:ReturnType<typeof setTimeout>;
  const loadPrefs=()=>reloadAutomatic().catch(()=>{if(!stopped)retry=setTimeout(loadPrefs,30000);});
  loadPrefs();
  const changed=(event:Event)=>{if((event as CustomEvent).detail===workspace)current.clock.changed(Date.now());};
  const tick=()=>{if(stopped||auto.current!==current||!current.prefs.enabled||!current.prefs.configured||startingRef.current||observed.current||!current.clock.due(Date.now()))return;
   start().catch(()=>setError(tr('Sincronizzazione automatica non avviata. Nuovo tentativo programmato.')));
  };
  const timer=setInterval(tick,1000);
  window.addEventListener('fuorigiri-archive-write',changed);
  return()=>{stopped=true;clearInterval(timer);clearTimeout(retry);window.removeEventListener('fuorigiri-archive-write',changed);if(auto.current===current)auto.current=null;};
 },[workspace]);
 const configureAutomatic=async(enabled:boolean)=>{
  const current=auto.current;
  const prefs=await api('sync/automatic',{enabled},'PUT',workspace);
  if(current&&auto.current===current&&current.workspace===workspace){auto.current.prefs=prefs;setAutomatic(prefs);if(enabled)auto.current.clock.next=Date.now();}
 };
 return {automatic,configureAutomatic,reloadAutomatic,job,starting,error,start,running:starting||job.status==='running'};
}
