import React,{useState,type FormEvent} from 'react';
import {Field,FormActions} from '@cycling-suite/ui';
import {tr} from './i18n';
type Row=Record<string,any>;
export function GroupEditor({groups,parentId='',onSubmit,busy}:{groups:Row[],parentId?:string,onSubmit:(e:FormEvent<HTMLFormElement>)=>void,busy:boolean}){
 const [parent,setParent]=useState(parentId);
 return <form onSubmit={onSubmit}><h2>{tr('Categoria o stagione')}</h2>
  <Field label={tr('Categoria padre')}><select name="parent_id" value={parent} onChange={e=>setParent(e.target.value)}><option value="">{tr('Categoria principale')}</option>{groups.filter(g=>!g.parent_id).map(g=><option key={g.id} value={g.id}>{g.name}</option>)}</select></Field>
  <Field label={tr('Nome categoria o gruppo')}><input name="name" required={!parent} autoFocus placeholder={parent?tr('Facoltativo per una stagione: usa il nome della categoria'):''}/></Field>
  {parent?<Field label={tr('Stagione')}><input name="season" required inputMode="numeric" pattern="[0-9]{4}" defaultValue={new Date().getFullYear()}/></Field>:<p>{tr('Crea la categoria, poi aggiungi le sue stagioni.')}</p>}
  <FormActions><button type="submit" className="primary" disabled={busy}>{tr('Salva')}</button></FormActions>
 </form>;
}
