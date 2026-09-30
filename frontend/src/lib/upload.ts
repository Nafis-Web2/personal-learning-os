const BASE=process.env.NEXT_PUBLIC_API_URL||"http://localhost:8000";
export async function uploadLearningFile(userId:string,file:File,meta:{assignmentId?:string;courseId?:string;title?:string}={}){
 const fd=new FormData(); fd.append("file",file);
 if(meta.assignmentId)fd.append("assignment_id",meta.assignmentId);
 if(meta.courseId)fd.append("college_course_id",meta.courseId);
 if(meta.title)fd.append("title",meta.title);
 const r=await fetch(`${BASE}/users/${userId}/uploads`,{method:"POST",body:fd});
 if(!r.ok)throw new Error(await r.text()); return r.json();
}
