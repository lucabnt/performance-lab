import {useLayoutEffect,useRef} from 'react';
import {previousScreen,type Screen} from './androidBackModel';

type BackWindow=Window&{fuorigiriBack?:()=>boolean};
export function useAndroidBack(enabled:boolean,page:string,selected:string,workspace:string,busy:boolean,restore:(screen:Screen)=>void){
 const current=useRef<Screen>({page,selected,scroll:0}),history=useRef<Screen[]>([]);
 const archive=useRef(workspace),restoring=useRef<Screen|null>(null);
 const callback=useRef(restore);callback.current=restore;
 const blocked=useRef(busy);blocked.current=busy;
 useLayoutEffect(()=>{
  if(!enabled)return;
  const next={page,selected,scroll:0};
  if(archive.current!==workspace){archive.current=workspace;history.current=[];restoring.current=null}
  else if(restoring.current){next.scroll=restoring.current.scroll;restoring.current=null}
  else if(page!==current.current.page||selected!==current.current.selected){
   history.current=page==='athletes'&&!selected?[]:[...history.current,current.current].slice(-32);
  }
  current.current=next;
  requestAnimationFrame(()=>window.scrollTo(0,next.scroll));
 },[enabled,page,selected,workspace]);
 useLayoutEffect(()=>{
  if(!enabled)return;
  const target=window as BackWindow;
  const scroll=()=>{current.current={...current.current,scroll:window.scrollY}};
  const back=()=>{
   if(blocked.current)return true;
   const next=previousScreen(current.current,history.current);
   if(!next)return false;
   history.current.pop();restoring.current=next;callback.current(next);return true;
  };
  target.fuorigiriBack=back;window.addEventListener('scroll',scroll,{passive:true});
  return()=>{if(target.fuorigiriBack===back)delete target.fuorigiriBack;window.removeEventListener('scroll',scroll)};
 },[enabled]);
 return ()=>((window as BackWindow).fuorigiriBack?.()??false);
}
