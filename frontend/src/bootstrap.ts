import './mobile';
import {initializeLanguage} from './i18n';
import {withDeadline} from './startupDeadline';
const params=new URLSearchParams(location.hash.slice(1));
if(params.has('token')){sessionStorage.setItem('fuorigiri-token',params.get('token')!);history.replaceState(null,'',location.pathname)}
const token=sessionStorage.getItem('fuorigiri-token')||'';
initializeLanguage(()=>withDeadline((async()=>{
 const response=await fetch('/api/v1/device/preferences',{headers:{'X-Fuorigiri-Token':token,'X-Fuorigiri-Workspace':''}});
 if(!response.ok)throw new Error('Device preferences unavailable');
 return response.json();
})(),5000,'Preferenze non disponibili')).catch(()=>{}).then(()=>import('./main')).catch(()=>{
 const root=document.getElementById('root');if(!root)return;
 const message=document.createElement('p');message.setAttribute('role','alert');message.textContent='Interfaccia non caricata. I dati locali sono conservati. Codice AVVIO-02.';
 const retry=document.createElement('button');retry.textContent='Riprova';retry.onclick=()=>location.reload();root.replaceChildren(message,retry);
});
