import {language} from './i18n';
const labels:Record<string,[string,string]>={
 map_w:['MAP operativa · W','Operational MAP · W'],map_alt_w:['MAP interpolata · W','Interpolated MAP · W'],map_wkg:['MAP relativa · W/kg','Relative MAP · W/kg'],
 threshold_w:['Watt Soglia · W','Threshold power · W'],threshold_wkg:['Soglia relativa · W/kg','Relative threshold · W/kg'],ftp_w:['FTP dichiarata · W','Declared FTP · W'],ftp_wkg:['FTP relativa · W/kg','Relative FTP · W/kg'],
 weight_kg:['Peso · kg','Weight · kg'],height_cm:['Statura · cm','Height · cm'],fthr_bpm:['FC di soglia (FTHR) · bpm','Threshold HR (FTHR) · bpm'],fc_max_test_bpm:['FC massima osservata · bpm','Observed maximum HR · bpm'],fc_max_reference_bpm:['FC massima di riferimento · bpm','Reference maximum HR · bpm'],
 rest_hr:['FC a riposo · bpm','Resting HR · bpm'],rest_after_s:['Durata riposo · s','Rest duration · s'],threshold_coefficient:['Coefficiente MAP → soglia','MAP to threshold coefficient'],rpe:['Sforzo percepito (RPE 1–10)','Perceived exertion (RPE 1–10)'],end_s:['Durata sforzo · s','Effort duration · s'],
 dichiarato:['Dichiarata','Declared'],stimata_da_map:['Stimata dalla MAP','Estimated from MAP'],warmup:['Riscaldamento','Warm-up'],increment:['Incremento','Increment'],recovery:['Recupero','Recovery'],cooldown:['Defaticamento','Cool-down']};
export const metricLabel=(key:string)=>labels[key]?.[language==='en'?1:0]||key.replaceAll('_',' ');
export const numberText=(v:any)=>v==null?'—':typeof v==='number'?new Intl.NumberFormat(language,{maximumFractionDigits:2}).format(v):v;
