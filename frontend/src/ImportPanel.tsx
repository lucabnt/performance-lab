import React,{useEffect,useState} from 'react';
import {DataTable} from '@cycling-suite/ui';
import {tr} from './i18n';

type Row=Record<string,any>;
const profiles:Record<string,string>={appartenenze:'Appartenenze storiche e future',atleti:'Anagrafiche atleti',antropometria:'Antropometria',test_aerobico:'Test aerobici',test_anaerobico:'Test anaerobici'};
const families:Record<string,string>={sprint:'Sprint breve',wingate15:'Wingate 15 s',wingate30:'Wingate 30 s'};
const cell=(key:string,label:string,render?:(row:Row)=>any)=>({key,label:tr(label),...(render?{render}:{})});

function columns(profile:string){
 if(profile==='appartenenze')return [cell('athlete_external_id','ID esterno'),cell('athlete_name','Atleta'),cell('start','Data inizio'),cell('end','Data fine'),cell('group_name','Gruppo'),cell('subgroup','Sottogruppo / stagione'),cell('category_year','Anno di categoria'),cell('notes','Note')];
 if(profile==='atleti')return [cell('external_id','ID esterno'),cell('surname','Cognome'),cell('name','Nome'),cell('birth_year','Anno di nascita'),cell('birth_confirmed','Nascita confermata',r=>tr(r.birth_confirmed?'Sì':'No')),cell('birth_source','Fonte'),cell('sex','Sesso'),cell('status','Stato',r=>tr(r.status==='active'?'Attivo':'Archiviato')),cell('notes','Note')];
 const athlete=[cell('athlete_external_id','ID atleta'),cell('athlete_name','Atleta'),cell('date','Data')];
 if(profile==='antropometria')return [...athlete,cell('import_action','Operazione',r=>tr(r.import_action==='integrate'?'Integra rilevazione':'Nuova rilevazione')),cell('added_fields','Campi da integrare',r=>(r.added_fields||[]).map((k:string)=>tr(({weight_kg:'Peso · kg',height_cm:'Statura · cm',perineal_height_cm:'Altezza perineale · cm'} as Record<string,string>)[k]||k)).join(', ')),cell('weight_kg','Peso · kg'),cell('height_cm','Statura · cm'),cell('perineal_height_cm','Altezza perineale · cm'),cell('source','Fonte del peso',r=>tr(r.source)),cell('origin','Origine')];
 const test=[cell('external_id','ID test'),...athlete,cell('protocol_code','Protocollo')];
 if(profile==='test_aerobico')return [...test,cell('map_w','MAP operativa · W',r=>r.analysis?.map_w??'—'),cell('threshold_w','Soglia · W',r=>r.analysis?.threshold_w??'—'),cell('fc_max_test_bpm','FC massima · bpm',r=>r.analysis?.fc_max_test_bpm??'—')];
 return [...test,cell('test_type','Tipo di test',r=>tr(families[r.test_type]||r.test_type||'Non documentato')),cell('duration_s','Durata · s',r=>r.analysis?.duration_s??'—'),cell('peak_w','Picco · W',r=>r.analysis?.peak_w??'—'),cell('mean_w','Media · W',r=>r.analysis?.mean_w??'—')];
}

export function ImportPanel({org,api,run,refresh,download,readOnly=false,allowedProfiles}:{org:string,api:any,run:any,refresh:any,download:any,readOnly?:boolean,allowedProfiles?:readonly string[]}){
 const choices=Object.entries(profiles).filter(([key])=>!allowedProfiles||allowedProfiles.includes(key));
 const [profile,setProfile]=useState(()=>allowedProfiles?.[0]??'atleti');
 const [result,setResult]=useState<Row|null>(null),[schemas,setSchemas]=useState<Row>({});
 useEffect(()=>{run(async()=>setSchemas(await api('import/schemas')))},[]);
 const ready=result?.ready_rows??result?.ready??0;
 const rows=(result?.preview||[]).map((r:Row)=>({...r,...(r.analysis?Object.fromEntries(['map_w','threshold_w','fc_max_test_bpm','duration_s','peak_w','mean_w'].map(k=>[k,r.analysis[k]])): {})}));
 return <section className="panel protocol">
  <h2>{tr('Importazione in blocco da CSV')}</h2>
  {choices.length>1?<label>{tr('Tipo di importazione')}<select value={profile} onChange={e=>{setProfile(e.target.value);setResult(null)}}>{choices.map(([key,label])=><option key={key} value={key}>{tr(label)}</option>)}</select></label>:<p>{tr(profiles[profile])}</p>}
  <div className="actions"><button onClick={()=>run(()=>download('import/template/'+profile,profile+'-modello.csv'))}>{tr('Scarica modello CSV vuoto')}</button>{profile==='appartenenze'&&<button onClick={()=>run(()=>download('import/example/appartenenze','appartenenze-esempio.csv'))}>{tr('Scarica CSV di esempio')}</button>}</div>
  <input key={profile} aria-label={tr('CSV da importare')} disabled={readOnly} type="file" accept=".csv" onChange={e=>{const file=e.target.files?.[0];setResult(null);if(file)run(async()=>{const form=new FormData();form.append('file',file);form.append('organization_id',org);form.append('profile',profile);setResult(await api('import/preview',form))})}}/>
  <details><summary>{tr('Istruzioni e formato CSV')}</summary>
  <p>{tr('Importa prima le anagrafiche. Per associare i dati agli atleti usa atleta_id, non il nome.')}</p>
  {profile==='appartenenze'&&<p>{tr('Una riga per appartenenza: lo stesso atleta può comparire in più stagioni. Sottogruppo identifica la stagione; i gruppi mancanti vengono proposti in anteprima. Gli esempi sono sintetici: sostituisci ID, nomi e date con i tuoi dati.')}</p>}
  {profile==='antropometria'&&<p>{tr('L’import completa solo le misure mancanti. Fonte e origine aiutano a riconoscere le rilevazioni: se differiscono, i valori precedenti sono conservati con un avviso non bloccante. Misure discordanti o integrazioni ambigue richiedono una correzione dal profilo.')}</p>}
  {profile!=='appartenenze'&&<p>{tr('Il modello contiene soltanto le intestazioni. Compila una riga per atleta, rilevazione o test; lascia vuoti i valori non disponibili.')}</p>}
  <p className="hint">{tr('Colonne obbligatorie:')} {schemas[profile]?.required.join(', ')}. {tr(schemas[profile]?.rule||'')}</p>
  {profile==='test_anaerobico'&&<p>{tr('Per nuovi protocolli compila tipo_test e durata_s: sprint (3–10 s), wingate15 (15 s), wingate30 (30 s). ANA-15-070 resta compatibile con i CSV storici. I risultati importati sono riepiloghi dichiarati, senza ricalcolo dai campioni.')}</p>}
  <details><summary>{tr('Colonne facoltative')}</summary><p>{schemas[profile]?.optional.join(', ')}</p></details>
  </details>
  {result&&<>
   <p>{result.rows} {tr('righe ·')} {ready} {tr('record pronti ·')} {result.skipped} {tr('già presenti')}</p>
   {!!result.new_groups?.length&&<p>{tr('Nuove categorie e stagioni:')} {result.new_groups.map((g:Row)=>[g.name,g.season].filter(Boolean).join(' / ')).join(', ')}</p>}
   {!!result.new_protocols?.length&&<p>{tr('Nuovi protocolli di archivio:')} {result.new_protocols.map((p:Row)=>p.code).join(', ')}</p>}
   {result.errors.length>0?<DataTable rows={result.errors} columns={[cell('row','Riga'),cell('error','Errore')]}/>:<p role="status">{tr('Nessun errore rilevato.')}</p>}
   {!!result.warnings?.length&&<><p role="status">{tr('Avvisi non bloccanti: conservati i dati descrittivi precedenti.')}</p><DataTable rows={result.warnings} columns={[cell('row','Riga'),cell('athlete_external_id','ID atleta'),cell('athlete_name','Atleta'),cell('date','Data'),cell('column','Campo',r=>tr(r.column==='peso_fonte'?'Fonte del peso':'Origine')),cell('previous','Valore conservato',r=>tr(r.previous||'—')),cell('incoming','Valore nel CSV',r=>tr(r.incoming||'—'))]}/></>}
   <DataTable rows={rows} columns={columns(profile)}/>
   <p>{tr('Record mostrati nell’anteprima:')} {result.preview.length} / {ready}</p>
   <button disabled={readOnly||result.errors.length>0||!ready} onClick={()=>run(async()=>{await api('import/commit',{organization_id:org,profile,staged_hash:result.staged_hash,plan_hash:result.plan_hash});setResult(null);await refresh()})}>{tr('Conferma importazione atomica')}</button>
  </>}
 </section>;
}
