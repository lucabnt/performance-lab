import {useEffect,useRef,useState,type ReactNode} from 'react';
import {language} from './i18n';
export function Dialog({title,children,onClose,wide=true,editor=false}:{title:string,children:ReactNode,onClose:()=>void,wide?:boolean,editor?:boolean}){
 const ref=useRef<HTMLElement>(null),dirty=useRef(false);const [prompt,setPrompt]=useState(false);
 const close=()=>{if(editor&&dirty.current)setPrompt(true);else onClose()};const callback=useRef(close);callback.current=close;
 useEffect(()=>{const previous=document.activeElement as HTMLElement|null;const overflow=document.body.style.overflow;document.body.style.overflow='hidden';const root=ref.current!;root.querySelector<HTMLButtonElement>('.close')?.focus();
 const key=(e:KeyboardEvent)=>{if(e.key==='Escape'){e.preventDefault();e.stopPropagation();callback.current()}if(e.key==='Tab'){const nodes=[...root.querySelectorAll<HTMLElement>('button,input,select,textarea,a[href],[tabindex="0"]')].filter(n=>!n.hasAttribute('disabled')&&n.getClientRects().length);const first=nodes[0],last=nodes.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last?.focus()}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first?.focus()}}};root.addEventListener('keydown',key);return()=>{document.body.style.overflow=overflow;root.removeEventListener('keydown',key);if(previous?.isConnected)previous.focus()};},[]);
 const en=language==='en';
 return <div className="overlay"><section ref={ref} role="dialog" aria-modal="true" aria-label={title} className={'dialog '+(wide?'wide':'')} onInputCapture={()=>{dirty.current=true}} onChangeCapture={()=>{dirty.current=true}} onClickCapture={e=>{const target=e.target as HTMLElement;if(target.closest('button')&&!target.closest('.dialog-toolbar'))dirty.current=true}}>
 <div className="dialog-toolbar"><strong>{title}</strong><button className="close" type="button" aria-label={en?'Close dialog':'Chiudi finestra'} onClick={close}>×</button></div>
 {prompt&&<div className="hint" role="alert"><p>{en?'Close and discard unsaved changes?':'Chiudere e perdere le modifiche non salvate?'}</p><div className="actions"><button onClick={()=>setPrompt(false)}>{en?'Continue editing':'Continua a modificare'}</button><button onClick={onClose}>{en?'Discard and close':'Scarta e chiudi'}</button></div></div>}{children}</section></div>
}
