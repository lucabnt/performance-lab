import {bodyMassIndex} from './anthropometryModel';
import {tr} from './i18n';

type Row=Record<string,any>;
export function AnthropometryBmiHistory({measurements,Plot}:{measurements:Row[];Plot:any}){
 const rows=measurements.filter(m=>bodyMassIndex(m)!=null).sort((a,b)=>a.date.localeCompare(b.date));
 return <><p className="hint">{tr('IMC = peso / statura² (kg/m²), calcolato solo da peso e statura della stessa rilevazione. La fonte resta quella dei dati originali. È un dato descrittivo: non misura la composizione corporea e non classifica salute o prestazione. Per i giovani l’interpretazione richiede riferimenti per età e sesso.')}</p>{rows.length>=2&&<details><summary>{tr('Storico IMC (BMI)')}</summary><Plot data={[{x:rows.map(m=>m.date),y:rows.map(bodyMassIndex),customdata:rows.map(m=>tr(m.source||'')),name:tr('IMC (BMI) · kg/m²'),type:'scatter',mode:'lines+markers',hovertemplate:'%{x}<br>%{y:.2f} kg/m²<br>%{customdata}<extra></extra>'}]} layout={{xaxis:{type:'date'},yaxis:{title:{text:'kg/m²'}}}}/></details>}</>;
}
