const BASE=process.env.NEXT_PUBLIC_API_URL||"http://localhost:8000";
export const DEV_USER=process.env.NEXT_PUBLIC_DEV_USER_ID||"";
export async function bootstrapDevUser(){return req<any>(`/dev/bootstrap`,{method:"POST"});}
async function req<T>(p:string,o:RequestInit={}):Promise<T>{const r=await fetch(BASE+p,{...o,headers:{"Content-Type":"application/json",...(o.headers||{})},cache:"no-store"});if(!r.ok)throw new Error(await r.text());return r.json()}
export const api={
 dashboard:(u:string)=>req<any>(`/users/${u}/dashboard`),
 external:(u:string,b:any)=>req<any>(`/users/${u}/external-learning`,{method:"POST",body:JSON.stringify(b)}),
 course:(u:string,b:any)=>req<any>(`/users/${u}/college-courses`,{method:"POST",body:JSON.stringify(b)}),
 homework:(u:string,b:any)=>req<any>(`/users/${u}/homework`,{method:"POST",body:JSON.stringify(b)}),
 resource:(u:string,b:any)=>req<any>(`/users/${u}/resources`,{method:"POST",body:JSON.stringify(b)}),
 note:(u:string,b:any)=>req<any>(`/users/${u}/notes`,{method:"POST",body:JSON.stringify(b)}),
 next:(u:string)=>req<any>(`/users/${u}/today/next`),
 integration:()=>req<any>(`/integration/status`),
 teacher:(u:string,mode:string,topic:string,help=0)=>req<any>(`/users/${u}/teacher/turn?mode=${encodeURIComponent(mode)}&topic=${encodeURIComponent(topic)}&help_level=${help}`,{method:"POST"}),
 personalization:(u:string,preferred="visual")=>req<any>(`/users/${u}/personalization/preview?preferred=${encodeURIComponent(preferred)}`,{method:"POST"}),
 liveTeacher:(u:string,b:any)=>req<any>(`/users/${u}/teacher/live`,{method:"POST",body:JSON.stringify(b)}),
 classroomTurn:(u:string,b:any)=>req<any>(`/users/${u}/teacher/classroom-turn`,{method:"POST",body:JSON.stringify(b)}),
 curriculum:()=>req<any[]>(`/curriculum`),
 startCourse:(u:string,c:string)=>req<any>(`/users/${u}/courses/${c}/start`,{method:"POST"}),
 coursePosition:(u:string,c:string)=>req<any>(`/users/${u}/courses/${c}/position`),
 advanceCourse:(u:string,c:string)=>req<any>(`/users/${u}/courses/${c}/advance`,{method:"POST"})
};