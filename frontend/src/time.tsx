import {useEffect,useRef,useState} from 'react';
import {language} from './i18n';
import {clock,parseClock} from './timeModel';
export {clock,parseClock} from './timeModel';
export function validTimes(target:HTMLElement){for(const input of target.closest('[role="dialog"]')?.querySelectorAll<HTMLInputElement>('.time-input input')||[]){if(!input.reportValidity())return false}return true}
export function TimeInput({label,value,onChange}:{label:string,value:any,onChange:(v:number|null)=>void}){
 const [text,setText]=useState(value==null||value===''?'':clock(Number(value)));const ref=useRef<HTMLInputElement>(null);
 useEffect(()=>{setText(value==null||value===''?'':clock(Number(value)));ref.current?.setCustomValidity('')},[value]);
 const invalid=!!text&&parseClock(text)==null;
 return <fieldset className="time-input"><legend>{label}</legend><label>{language==='en'?'Seconds':'Secondi'}<input aria-label={label+' · s'} type="number" min="0" step="any" value={value??''} onChange={e=>onChange(e.target.value===''?null:Number(e.target.value))}/></label><label>mm:ss<input ref={ref} aria-label={label+' · mm:ss'} value={text} placeholder="23:45" aria-invalid={invalid} onChange={e=>{setText(e.target.value);const t=parseClock(e.target.value);e.target.setCustomValidity(e.target.value&&t==null?'Usa mm:ss (es. 23:45)':'');if(t!=null)onChange(t);else if(!e.target.value)onChange(null)}}/></label>{invalid&&<small role="alert">{language==='en'?'Use minutes:seconds, e.g. 23:45.':'Usa minuti:secondi, per esempio 23:45.'}</small>}</fieldset>
}
