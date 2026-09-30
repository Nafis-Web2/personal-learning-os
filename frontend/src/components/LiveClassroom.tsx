"use client";
import {useEffect,useState} from "react";
import {getClassroom} from "../lib/classroom";
import {api} from "../lib/api";

const copy:any={
 daily_gate:["Daily Gate","Show me what you still remember.","Teach the previous lesson back without looking anything up."],
 repair:["Repair first","A gap needs attention before moving on.","We’ll target the weak part, practice it, and retest only what needs repair."],
 spaced_review:["Spaced review","Strengthen an older concept.","Try from memory before opening notes or hints."],
 continue_lesson:["Continue learning","You’re ready for the next lesson.","Continue from your saved curriculum position."],
 choose_course:["Choose what to learn","Your classroom is ready.","Pick a course or add one to begin."]
};
export default function LiveClassroom({userId,courseId}:{userId:string,courseId?:string}){
 const [s,setS]=useState<any>(null),[err,setErr]=useState(""),[input,setInput]=useState(""),[busy,setBusy]=useState(false);
 const [turns,setTurns]=useState<any[]>([]),[position,setPosition]=useState<any>(null);
 useEffect(()=>{getClassroom(userId,courseId).then(async x=>{setS(x);if(x.active_course?.id)setPosition(await api.coursePosition(userId,x.active_course.id))}).catch(e=>setErr(e.message))},[userId,courseId]);
 async function send(mode?:string,helpLevel=0){
  if(!input.trim()&&mode!=="teach")return;
  setBusy(true);setErr("");
  try{
   const chosen=mode||((s?.next_action==="daily_gate")?"daily_gate":s?.next_action==="repair"?"repair":"teach");
   const mine=input.trim();if(mine)setTurns(v=>[...v,{role:"learner",text:mine}]);
   const r=await api.classroomTurn(userId,{message:mine,mode:chosen,help_level:helpLevel,course_id:s?.active_course?.id||null});
   setTurns(v=>[...v,{role:"teacher",text:r.message,meta:`${r.provider} · ${r.mode}`,evidence:r.evidence_result}]);setInput("");
   const refreshed=await getClassroom(userId,courseId);setS(refreshed);
  }catch(e:any){setErr(e.message)}finally{setBusy(false)}
 }
 if(err&&!s)return <div className="card"><b>Classroom could not load.</b><p className="muted">{err}</p></div>;
 if(!s)return <div className="card"><p className="muted">Loading your learning state…</p></div>;
 const [tag,title,desc]=copy[s.next_action]||copy.continue_lesson;
 return <div className="classroom">
  <section className="card teacher">
   <div className="eyebrow">{tag}</div><h2>{position?.active_concept?.name||title}</h2>{position?.module&&<p><b>{position.module.code} · {position.module.title}</b> → {position.lesson?.title}</p>}<p className="muted">{desc}</p>
   <div className="conversation">
    {turns.length===0&&<div className="soft"><b>Your AI Teacher is ready.</b><p className="muted">It sees your saved lesson position, mastery, due reviews and unresolved learning gaps. Journal text is included only when your privacy setting permits it.</p></div>}
    {turns.map((t,i)=><div key={i} className={`turn ${t.role}`}><b>{t.role==="teacher"?"Teacher":"You"}</b><p>{t.text}</p>{t.meta&&<small className="muted">{t.meta}</small>}{t.evidence?.mastery_updated&&<div className="soft"><b>Learning evidence accepted</b><p className="muted">Mastery updated · Review scheduled{t.evidence.repair_opened?" · Repair opened":""}</p></div>}{t.evidence?.evaluated&&!t.evidence?.accepted&&<small className="muted">No mastery change: {t.evidence.reason}</small>}</div>)}
   </div>
   <textarea className="answer" value={input} onChange={e=>setInput(e.target.value)} placeholder={s.next_action==="daily_gate"?"Teach it back here without notes…":"Ask, explain, solve, or show your work…"} />
   <div className="actions">
    <button className="btn primary" disabled={busy||!input.trim()} onClick={()=>send()}>{busy?"Thinking…":s.next_action==="daily_gate"?"Submit explanation":"Send to Teacher"}</button>
    {s.next_action!=="daily_gate"&&<button className="btn" disabled={busy} onClick={()=>send("teach",1)}>Give me a small hint</button>}
   </div>
   {err&&<p className="muted">{err}</p>}
  {position?.active_concept&&<div className="soft" style={{marginTop:14}}><b>Mastery gate</b><p className="muted">Understanding and Application must each reach 70% before progression. A conversation alone never unlocks the next lesson.</p><button className="btn" onClick={async()=>{const r=await api.advanceCourse(userId,s.active_course.id);if(r.advanced){setPosition(await api.coursePosition(userId,s.active_course.id));setS(await getClassroom(userId,courseId))}else setErr(r.reason==="mastery_not_ready"?"Keep practicing this concept before continuing.":r.reason)}}>Continue when ready →</button></div>}</section>
  <aside className="grid">
   <div className="card"><div className="eyebrow">CURRENT POSITION</div><h3>{s.position?.lesson_title||"Course start"}</h3><p className="muted">{s.active_course?.title||"Choose a course to begin."}</p></div>
   <div className="card"><div className="eyebrow">TUTOR AWARENESS</div>
    <div className="row"><span>Due reviews</span><b>{s.due_reviews?.length||0}</b></div>
    <div className="row"><span>Open misconceptions</span><b>{s.misconceptions?.length||0}</b></div>
    <div className="row"><span>Possible prerequisite gaps</span><b>{s.weak_prerequisite_candidates?.length||0}</b></div>
    <div className="row"><span>Recent help level</span><b>{s.independence?.recent_help_average??0}</b></div>
   </div>
   <div className="card"><div className="eyebrow">VISUAL SUPPORT</div><div className="visual"><b>Visuals follow the lesson.</b><p className="muted">Graphs, diagrams, code traces and interactive explanations appear when useful.</p></div></div>
  </aside>
 </div>
}