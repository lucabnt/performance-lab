type Selection={workspace:string;organization:string};
type Row=Record<string,any>;

/** Ignore responses from a previous selection; recover stale IDs after a demo reset. */
export async function loadArchiveSelection(api:any,read:()=>Selection,write:(selection:Selection)=>void,isCurrent=()=>true){
 const requested=read();
 const unchanged=(expected:Selection)=>{const now=read();return isCurrent()&&now.workspace===expected.workspace&&now.organization===expected.organization};
 // The archive inventory must remain readable even when a remembered ID disappeared.
 const workspaces:Row[]=await api('workspaces',undefined,'GET','');
 if(!unchanged(requested))return null;
 const missing=!!requested.workspace&&!workspaces.some(w=>w.id===requested.workspace);
 const expected=missing?{workspace:'',organization:''}:requested;
 if(missing)write(expected);
 const state=await api('state',undefined,'GET',expected.workspace);
 if(!unchanged(expected))return null;
 const organization=state.organization.some((o:Row)=>o.id===expected.organization)?expected.organization:state.organization[0]?.id||'';
 write({workspace:expected.workspace,organization});
 return {workspaces,state,workspace:expected.workspace,organization,missing};
}
