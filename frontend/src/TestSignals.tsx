import {tr} from './i18n';
import {useState} from 'react';
import {buildSignalChart,hasRecordedTrace,type SignalRow} from './signalChartModel';

/** One overlaid timeline; observed values retain independent physical units. */
export function TestSignals({test,protocol,Plot,onPick}:{test:SignalRow;protocol?:SignalRow;Plot:any;onPick?:(t:number)=>void}){
 const [selected,setSelected]=useState<string[]|null>(null);
 const available=buildSignalChart(test,protocol).availableChannels;
 const core=available.filter(c=>['power','hr','cadence','vo2_l_min'].includes(c.key));
 const keys=selected??(core.length?core:available).map(c=>c.key);
 const model=buildSignalChart(test,protocol,keys);
 return <section className="test-signals" aria-label={tr("Grafici del test")}>
  <h3>{tr("Tracciato e misure registrate")}</h3>
  {available.length>0&&<fieldset className="signal-options"><legend>{tr("Canali sovrapposti")}</legend>{available.map(c=><label key={c.key}><input type="checkbox" checked={keys.includes(c.key)} onChange={e=>setSelected(e.target.checked?[...keys,c.key]:keys.filter(k=>k!==c.key))}/>{c.label} · {c.unit}</label>)}</fieldset>}
  {(model.channels.length>0||model.lactate.length>0)&&<Plot onPick={onPick} data={model.data} layout={model.layout}/>}
  {model.samples.length>0?<p className="muted">{model.samples.length} campioni. Linee sovrapposte con scale indipendenti e unità indicate sugli assi; le altezze di canali diversi non rappresentano valori equivalenti. Le bande evidenziano lo sforzo e le esclusioni motivate.</p>:<p className="hint">{hasRecordedTrace(test)?'Il file è associato al test ma i campioni non sono disponibili: verificare l’importazione e l’archivio.':'Questo test contiene solo risultati riepilogativi manuali: non ci sono campioni temporali FIT/CSV da rappresentare. Potenza, FC e cadenza medie o massime non permettono di ricostruire una curva.'}</p>}
  {model.samples.length>0&&!model.channels.length&&!model.lactate.length&&<p className="hint">Seleziona un canale disponibile per visualizzare il tracciato.</p>}
  {model.lactate.length>0&&<p className="muted">Lattato: punti misurati all’istante del prelievo, senza interpolazione temporale. L’associazione al carico e i metodi di soglia sono riportati separatamente.</p>}
 </section>;
}
