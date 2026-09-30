"use client";
import {useMemo,useRef,useState} from "react";
import {uploadLearningFile} from "../lib/upload";

export default function HomeworkUpload({userId,assignmentId,courseId,onDone}:{userId:string;assignmentId?:string;courseId?:string;onDone?:()=>void}){
 const [files,setFiles]=useState<File[]>([]),[busy,setBusy]=useState(false),[error,setError]=useState("");
 const input=useRef<HTMLInputElement>(null);
 const previews=useMemo(()=>files.map(f=>({file:f,url:f.type.startsWith("image/")?URL.createObjectURL(f):null})),[files]);
 function add(list:FileList|null){if(!list)return;setFiles(x=>[...x,...Array.from(list)].slice(0,12))}
 async function send(){setBusy(true);setError("");try{for(const f of files)await uploadLearningFile(userId,f,{assignmentId,courseId,title:f.name});setFiles([]);onDone?.()}catch(e:any){setError(e.message)}finally{setBusy(false)}}
 return <section className="uploadCard">
  <input ref={input} hidden type="file" accept="image/jpeg,image/png,image/webp,application/pdf" multiple capture="environment" onChange={e=>add(e.target.files)}/>
  <button type="button" className="dropZone" onClick={()=>input.current?.click()}
   onDragOver={e=>e.preventDefault()} onDrop={e=>{e.preventDefault();add(e.dataTransfer.files)}}>
   <strong>📷 Add homework pictures</strong><span>Take a photo, choose images, or drop files here</span><small>JPG, PNG, WEBP or PDF · up to 15 MB each</small>
  </button>
  {previews.length>0&&<div className="previewGrid">{previews.map((p,i)=><div className="preview" key={i}>
   {p.url?<img src={p.url} alt={`Homework page ${i+1}`}/>:<div className="pdf">PDF<br/>Page file</div>}
   <button aria-label="Remove file" onClick={()=>setFiles(x=>x.filter((_,j)=>j!==i))}>×</button>
   <small>Page {i+1}</small>
  </div>)}</div>}
  {files.length>0&&<button className="btn primary" disabled={busy} onClick={send}>{busy?"Uploading…":`Upload ${files.length} ${files.length===1?"page":"pages"}`}</button>}
  {error&&<p className="uploadError">{error}</p>}
 </section>
}
