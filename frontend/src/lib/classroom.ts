const BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:8000";
export async function getClassroom(userId:string,courseId?:string){
 const q=courseId?`?course_id=${encodeURIComponent(courseId)}`:"";
 const r=await fetch(`${BASE}/users/${userId}/classroom${q}`,{cache:"no-store"});
 if(!r.ok)throw new Error(await r.text()); return r.json();
}
