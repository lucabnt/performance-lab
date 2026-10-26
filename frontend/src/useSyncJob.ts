import {useEffect,useRef,useState} from 'react';
type Row=Record<string,any>;
export function useSyncJob(api:any,workspace:string,onFinished:()=>void){
 const [job,setJob]=useState<Row>({status:'idle'}),[starting,setStarting]=useState(false),[error,setError]=useState('');
 const generation=useRef(0),startingRef=useRef(false),finished=useRef(onFinished),observed=useRef('');
 const wake=useRef<(()=>void)|null>(null);
 finished.current=onFinished;
 const accept=(next:Row)=>{setJob(next);setError('');if(next.status==='running')observed.current=next.id;else if(observed.current===next.id){observed.current='';finished.current()}};
 useEffect(()=>{const current=++generation.current;let stopped=false,timer:ReturnType<typeof setTimeout>;
  setJob({status:'idle'});setError('');observed.current='';
  if(!workspace)return;
  const poll=async()=>{try{const next=await api('sync/job',undefined,'GET',workspace);if(stopped||current!==generation.current)return;
    if(!observed.current||next.id===observed.current)accept(next);
    clearTimeout(timer);timer=setTimeout(poll,next.status==='running'||observed.current?1200:6000);
   }catch(e){if(stopped)return;if(observed.current)setError((e as Error).message);timer=setTimeout(poll,observed.current?2500:10000)}};
  wake.current=()=>{clearTimeout(timer);timer=setTimeout(poll,50)};
  poll();return()=>{stopped=true;clearTimeout(timer);wake.current=null};
 },[workspace]);
 const start=async(verify_all=false)=>{
  if(startingRef.current)return;
  startingRef.current=true;setStarting(true);const current=generation.current;
  try{const next=await api('sync/start',{verify_all},'POST',workspace);if(current===generation.current){observed.current=next.id;accept(next);wake.current?.()}}finally{startingRef.current=false;setStarting(false)}
 };
 return {job,starting,error,start,running:starting||job.status==='running'};
}
