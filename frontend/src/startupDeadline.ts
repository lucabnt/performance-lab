/** A stalled bridge must not leave the startup screen spinning indefinitely. */
export function withDeadline<T>(task:Promise<T>,milliseconds:number,message:string):Promise<T>{
 return new Promise((resolve,reject)=>{
  const timer=setTimeout(()=>reject(new Error(message)),milliseconds);
  task.then(value=>{clearTimeout(timer);resolve(value)},error=>{clearTimeout(timer);reject(error)});
 });
}
