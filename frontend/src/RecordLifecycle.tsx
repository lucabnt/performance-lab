import {useState} from 'react';
import {DataTable,FormActions} from '@cycling-suite/ui';
import {Dialog} from './Dialog';
import {tr} from './i18n';

type Row=Record<string,any>;

/** Shared product workflow outside the editor's form, so deletion needs no valid draft. */
export function RecordDeletion({record,busy,canEdit,error,onDelete}:{record:Row;busy:boolean;canEdit:boolean;error:string;onDelete:()=>void}){
 const [confirm,setConfirm]=useState(false);
 const label=record.kind==='measurement'?'Elimina rilevazione':'Elimina test';
 return <><button type="button" disabled={!canEdit||busy} onClick={()=>setConfirm(true)}>{tr(label)}</button>{confirm&&<Dialog title={tr(label)} busy={busy} onClose={()=>setConfirm(false)}>
  <p>{tr('Data')}: {record.date}</p>
  <p>{tr('L’elemento sarà escluso dagli elenchi e dai calcoli correnti. Potrai ripristinarlo dalla sezione degli elementi eliminati. Le revisioni, i file originali e le analisi già conservate rimangono disponibili.')}</p>
  {error&&<p role="alert">{error}</p>}
  <FormActions><button type="button" disabled={busy} onClick={()=>setConfirm(false)}>{tr('Annulla')}</button><button type="button" disabled={!canEdit||busy} onClick={onDelete}>{tr('Conferma eliminazione')}</button></FormActions>
 </Dialog>}</>;
}

export function DeletedRecords({records,title,describe,busy,canEdit,onRestore}:{records:Row[];title:string;describe:(r:Row)=>string;busy:boolean;canEdit:boolean;onRestore:(r:Row)=>void}){
 if(!records.length)return null;
 return <details className="panel"><summary>{tr(title)} · {records.length}</summary><DataTable rows={records} columns={[
  {key:'date',label:tr('Data')},
  {key:'description',label:tr('Dettagli'),render:r=>describe(r)},
  {key:'restore',label:tr('Azioni'),render:r=><button type="button" disabled={!canEdit||busy} onClick={()=>onRestore(r)}>{tr('Ripristina')}</button>},
 ]}/></details>;
}
