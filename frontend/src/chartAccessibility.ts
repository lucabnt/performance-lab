type Trace={name?:string;x?:unknown[];y?:unknown[]};
const numeric=(v:unknown):v is number=>typeof v==='number'&&Number.isFinite(v);
export function chartSummary(data:Trace[]){return data.map(t=>{let count=0,min:number|null=null,max:number|null=null;for(const v of t.y||[])if(numeric(v)){count++;min=min===null?v:Math.min(min,v);max=max===null?v:Math.max(max,v)}return {name:t.name||'—',count,min,max}})}
/** Bounded DOM even for long FIT traces: no substitution for missing observations. */
export function chartTablePage(data:Trace[],requested:number,size=30){
 const total=data.reduce((n,t)=>n+(t.y?.length||0),0),page=Math.max(0,Math.min(requested,Math.max(0,Math.ceil(total/size)-1))),rows:{name:string;x:unknown;y:unknown}[]=[];
 let offset=0;const start=page*size,end=start+size;
 for(const trace of data){const values=trace.y||[],a=Math.max(0,start-offset),b=Math.min(values.length,end-offset);for(let i=a;i<b;i++)rows.push({name:trace.name||'—',x:trace.x?.[i]??null,y:values[i]??null});offset+=values.length;if(offset>=end)break}
 return {rows,page,total};
}
