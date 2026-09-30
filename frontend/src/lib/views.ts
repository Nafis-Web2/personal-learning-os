const BASE=process.env.NEXT_PUBLIC_API_URL||"http://localhost:8000";
async function get(p:string){const r=await fetch(BASE+p,{cache:"no-store"});if(!r.ok)throw new Error(await r.text());return r.json()}
export const views={
 mastery:(u:string)=>get(`/users/${u}/mastery-view`),
 roadmaps:(u:string)=>get(`/users/${u}/roadmaps-view`),
 progress:(u:string)=>get(`/users/${u}/progress-view`),
 journal:(u:string)=>get(`/users/${u}/journal-view`)
};