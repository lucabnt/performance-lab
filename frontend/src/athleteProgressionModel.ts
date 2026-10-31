type Row=Record<string,any>;
export function progressionSeries(tests:Row[],protocols:Row[],metric:string){
 const buckets=new Map<string,Row>();
 for(const t of [...tests].sort((a,b)=>a.date.localeCompare(b.date)||a.id.localeCompare(b.id))){
  const a=t.analysis;
  const valid=typeof a[metric]==='number'&&Number.isFinite(a[metric])&&!(metric.endsWith('wkg')&&t.settings?.weight_source==='stimato');
  const source=a.threshold_source||'n.d.';
  const method=a.comparison_key||JSON.stringify([a.preset?.hash,a.engine,a.source,a.gas?.source,a.gas?.vo2peak?.method_id,t.settings?.conditions||{}]);
  const id=JSON.stringify([t.protocol_id,method,source]);
  if(!buckets.has(id)){
   const p=protocols.find(p=>p.id===t.protocol_id);
   buckets.set(id,{id,title:(p?.name||'Protocollo')+' · '+(p?.version||'?'),method:a.preset?.name||({computed:'Calcolato dal tracciato',manual:'Dichiarato manualmente','legacy-csv':'Storico CSV'} as Row)[a.source]||'Metodo storico',source,valid:0,tests:[]});
  }
  buckets.get(id)!.tests.push(valid?t:{...t,analysis:{...a,[metric]:null}});
  if(valid)buckets.get(id)!.valid++;
 }
 return [...buckets.values()].filter(s=>s.valid>0).sort((a,b)=>b.valid-a.valid||a.id.localeCompare(b.id)).map((s,i):Row=>({...s,code:'S'+(i+1)}));
}
