"use client";
import {useEffect,useState} from "react";
import {api} from "../lib/api";
export function LearningHome({userId,onOpen}:{userId:string,onOpen:(courseId:string)=>void}){
 const [courses,setCourses]=useState<any[]>([]),[busy,setBusy]=useState("");
 useEffect(()=>{api.curriculum().then(setCourses)},[]);
 async function start(c:any){setBusy(c.id);try{await api.startCourse(userId,c.id);onOpen(c.id)}finally{setBusy("")}}
 return <div className="grid two">{courses.map(c=><div className="card" key={c.id}><div className="eyebrow">{c.code==="PYTHON-FOUNDATIONS"?"AI CAREER":"TRADING"}</div><h3>{c.title}</h3><p className="muted">{c.modules.length} modules · persistent progress · mastery-gated</p><div className="soft"><b>{c.modules[0]?.title}</b><p className="muted">{c.modules[0]?.lessons?.[0]?.title}</p></div><button className="btn primary" disabled={busy===c.id} onClick={()=>start(c)}>{busy===c.id?"Opening…":"Start / Continue →"}</button></div>)}</div>
}
export function CurriculumRoadmaps({userId,onOpen}:{userId:string,onOpen:(courseId:string)=>void}){
 const [courses,setCourses]=useState<any[]>([]);
 useEffect(()=>{api.curriculum().then(setCourses)},[]);
 return <div className="grid two">{courses.map(c=><div className="card" key={c.id}><div className="eyebrow">BUILT-IN ROADMAP</div><h2>{c.title}</h2>{c.modules.map((m:any)=><details key={m.id}><summary><b>{m.code} · {m.title}</b></summary><div style={{padding:"8px 0 10px 12px"}}>{m.lessons.map((l:any)=><div key={l.id}><span>{l.title}</span><small className="muted"> · {l.concepts.length} concepts</small></div>)}</div></details>)}<button className="btn primary" onClick={async()=>{await api.startCourse(userId,c.id);onOpen(c.id)}}>Start / Continue →</button></div>)}</div>
}