from datetime import datetime,timedelta
from app.models import Enrollment,Course,Module,Lesson,Concept,ConceptMastery,EvidenceEvent,StudySession,JournalEntry,PrivacySetting,ReviewSchedule

def mastery_view(db,user_id):
    rows=db.query(ConceptMastery).filter_by(user_id=user_id).all()
    def band(v): return "Durable" if v>=95 else "Strong" if v>=85 else "Proficient" if v>=70 else "Developing" if v>=50 else "New"
    out=[]
    for x in sorted(rows,key=lambda r:r.overall or 0):
        c=db.get(Concept,x.concept_id); out.append({"concept_id":x.concept_id,"concept":getattr(c,"name",x.concept_id),"overall":x.overall,"band":band(x.overall or 0),"recall":x.recall,"understanding":x.understanding,"application":x.application,"transfer":x.transfer,"independence":x.independence,"retention":x.retention})
    return {"concepts":out}
def roadmaps_view(db,user_id):
    out=[]
    for e in db.query(Enrollment).filter_by(user_id=user_id,active=True).all():
        c=db.get(Course,e.course_id); l=db.get(Lesson,e.current_lesson_id) if e.current_lesson_id else None; m=db.get(Module,l.module_id) if l else None
        out.append({"course_id":e.course_id,"course":getattr(c,"title","Course"),"module":getattr(m,"title",None),"lesson":getattr(l,"title",None)})
    return {"courses":out}
def progress_view(db,user_id):
    since=datetime.utcnow()-timedelta(days=30); sessions=db.query(StudySession).filter(StudySession.user_id==user_id,StudySession.started_at>=since).all(); evidence=db.query(EvidenceEvent).filter(EvidenceEvent.user_id==user_id,EvidenceEvent.created_at>=since).count(); due=db.query(ReviewSchedule).filter(ReviewSchedule.user_id==user_id,ReviewSchedule.next_due_at<=datetime.utcnow()).count()
    minutes=sum(max(0,int((s.ended_at-s.started_at).total_seconds()/60)) for s in sessions if s.ended_at)
    return {"window_days":30,"study_sessions":len(sessions),"study_minutes":minutes,"evidence_events":evidence,"reviews_due":due}
def journal_view(db,user_id):
    p=db.get(PrivacySetting,user_id); entries=db.query(JournalEntry).filter_by(user_id=user_id).order_by(JournalEntry.created_at.desc()).limit(10).all()
    return {"ai_access":p.journal_ai_access if p else "private","entries":[{"id":e.id,"kind":e.entry_type,"created_at":e.created_at.isoformat(),"preview":e.body[:140]} for e in entries]}
