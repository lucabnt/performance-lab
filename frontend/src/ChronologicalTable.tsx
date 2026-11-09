import React,{useState,type ReactNode,type ReactElement} from 'react';
import {language} from './i18n';

// Product list policy: all dated rows are ordered before taking a page.
export function ChronologicalTable({children,label,pageIndex,onPageChange}:{children:ReactNode;label:string;pageIndex?:number;onPageChange?:(page:number)=>void}){
 const [localPage,setLocalPage]=useState(0);
 const sections=React.Children.toArray(children) as ReactElement<any>[];
 const body=sections.find(s=>s.type==='tbody');
 const dateOf=(row:ReactElement<any>)=>String((React.Children.toArray(row.props.children)[0] as ReactElement<any>).props.children);
 const rows=(React.Children.toArray(body?.props.children) as ReactElement<any>[]).sort((a,b)=>dateOf(b).localeCompare(dateOf(a)));
 const last=Math.max(0,Math.ceil(rows.length/15)-1),page=Math.max(0,Math.min(pageIndex??localPage,last));
 const move=(value:number)=>{setLocalPage(value);onPageChange?.(value)};
 const en=language==='en';
 return <><div className="table-scroll"><table>{sections.map(section=>section.type==='tbody'?React.cloneElement(section,{children:rows.slice(page*15,(page+1)*15)}):section)}</table></div>{rows.length>15&&<nav className="suite-pagination" aria-label={label}><button type="button" disabled={page===0} onClick={()=>move(page-1)}>{en?'Previous':'Precedenti'}</button><span role="status">{page*15+1}–{Math.min((page+1)*15,rows.length)} / {rows.length}</span><button type="button" disabled={page===last} onClick={()=>move(page+1)}>{en?'Next':'Successivi'}</button></nav>}</>;
}
