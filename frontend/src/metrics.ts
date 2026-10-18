import {language} from './i18n';
const labels:Record<string,[string,string]>={
"peak_w":["Picco dichiarato / finestra protocollo (W)", "Picco dichiarato / finestra protocollo (W)"],
"peak_wkg":["Picco / peso (W/kg)", "Picco / peso (W/kg)"],
"best_1s_w":["Migliori 1 s (W)", "Migliori 1 s (W)"],
"best_5s_w":["Migliori 5 s (W)", "Migliori 5 s (W)"],
"time_to_peak_s":["Tempo al picco (s)", "Tempo al picco (s)"],
"mean_w":["Potenza media (W)", "Potenza media (W)"],
"mean_wkg":["Potenza media / peso (W/kg)", "Potenza media / peso (W/kg)"],
"work_kj":["Lavoro meccanico osservato (kJ)", "Lavoro meccanico osservato (kJ)"],
"end_power_w":["Potenza finale (W)", "Potenza finale (W)"],
"fatigue_pct":["Calo picco-finale (%)", "Calo picco-finale (%)"],
"decline_ws":["Pendenza picco-finale (W/s)", "Pendenza picco-finale (W/s)"],
"declared_fatigue_ws":["Indice di fatica storico, formula non verificata (W/s)", "Indice di fatica storico, formula non verificata (W/s)"],
"cadence_max_rpm":["Cadenza massima (rpm)", "Cadenza massima (rpm)"],
"cadence_mean_rpm":["Cadenza media (rpm)", "Cadenza media (rpm)"],

 lactate_2_w:['Potenza a 2 mmol/L · W','Power at 2 mmol/L · W'],lactate_4_w:['Potenza a 4 mmol/L · W','Power at 4 mmol/L · W'],vo2peak_l_min:['VO₂peak · L/min','VO₂peak · L/min'],vo2peak_ml_kg_min:['VO₂peak · mL/kg/min','VO₂peak · mL/kg/min'],
 map_w:['MAP operativa · W','Operational MAP · W'],map_alt_w:['MAP interpolata · W','Interpolated MAP · W'],map_wkg:['MAP relativa · W/kg','Relative MAP · W/kg'],
 threshold_w:['Watt Soglia · W','Threshold power · W'],threshold_wkg:['Soglia relativa · W/kg','Relative threshold · W/kg'],ftp_w:['FTP dichiarata · W','Declared FTP · W'],ftp_wkg:['FTP relativa · W/kg','Relative FTP · W/kg'],
 weight_kg:['Peso · kg','Weight · kg'],height_cm:['Statura · cm','Height · cm'],fthr_bpm:['FC di soglia (FTHR) · bpm','Threshold HR (FTHR) · bpm'],fc_max_test_bpm:['FC massima osservata · bpm','Observed maximum HR · bpm'],fc_max_reference_bpm:['FC massima di riferimento · bpm','Reference maximum HR · bpm'],
 rest_hr:['FC a riposo · bpm','Resting HR · bpm'],rest_after_s:['Durata riposo · s','Rest duration · s'],threshold_coefficient:['Coefficiente MAP → soglia','MAP to threshold coefficient'],rpe:['Sforzo percepito (RPE)','Perceived exertion (RPE)'],end_s:['Durata sforzo · s','Effort duration · s'],
 dichiarato:['Dichiarata','Declared'],stimata_da_map:['Stimata dalla MAP','Estimated from MAP'],warmup:['Riscaldamento','Warm-up'],increment:['Incremento','Increment'],recovery:['Recupero','Recovery'],cooldown:['Defaticamento','Cool-down']};
export const metricLabel=(key:string)=>labels[key]?.[language==='en'?1:0]||key.replaceAll('_',' ');
export const numberText=(v:any)=>v==null?'—':typeof v==='number'?new Intl.NumberFormat(language,{maximumFractionDigits:2}).format(v):v;
