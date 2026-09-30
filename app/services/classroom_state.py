from datetime import datetime
from app.models import Enrollment, Course, Module, Lesson, DailyGate, ReviewSchedule, Misconception, ConceptMastery, HelpEvent

def build_classroom_state(db,user_id:str,course_id:str|None=None):
    enrollments=db.query(Enrollment).filter_by(user_id=user_id,active=True).all()
    if not enrollments: return {"next_action":"choose_course","active_course":None,"position":None,"gate":None,"due_reviews":[],"misconceptions":[],"weak_prerequisite_candidates":[],"independence":{"recent_help_average":0,"samples":0}}
    active=next((e for e in enrollments if e.course_id==course_id),enrollments[0]); cid=active.course_id
    course=db.get(Course,cid); lesson=db.get(Lesson,active.current_lesson_id) if active.current_lesson_id else None; module=db.get(Module,lesson.module_id) if lesson else None
    gate=db.query(DailyGate).filter(DailyGate.user_id==user_id,DailyGate.course_id==cid,DailyGate.status.in_(["pending","partial","fail"])).order_by(DailyGate.created_at.desc()).first()
    reviews=db.query(ReviewSchedule).filter(ReviewSchedule.user_id==user_id,ReviewSchedule.next_due_at<=datetime.utcnow()).order_by(ReviewSchedule.next_due_at.asc()).limit(5).all()
    misconceptions=db.query(Misconception).filter_by(user_id=user_id,resolved=False).limit(5).all()
    mastery=db.query(ConceptMastery).filter_by(user_id=user_id).all(); weak=[m for m in mastery if min(m.understanding or 0,m.application or 0)<70][:5]
    helps=db.query(HelpEvent).filter_by(user_id=user_id).order_by(HelpEvent.created_at.desc()).limit(20).all(); levels=[h.level for h in helps]
    action="repair" if gate and gate.status in ("partial","fail") else "daily_gate" if gate else "spaced_review" if reviews else "continue_lesson"
    return {"next_action":action,"active_course":{"id":cid,"code":getattr(course,"code",None),"title":getattr(course,"title",None)},"position":{"module_id":getattr(module,"id",None),"module_title":getattr(module,"title",None),"lesson_id":getattr(lesson,"id",None),"lesson_title":getattr(lesson,"title",None)},"gate":None if not gate else {"id":gate.id,"status":gate.status,"created_at":gate.created_at.isoformat()},"due_reviews":[{"concept_id":r.concept_id,"due_at":r.next_due_at.isoformat()} for r in reviews],"misconceptions":[{"id":m.id,"concept_id":m.concept_id,"summary":m.description} for m in misconceptions],"weak_prerequisite_candidates":[{"concept_id":m.concept_id,"understanding":m.understanding,"application":m.application} for m in weak],"independence":{"recent_help_average":round(sum(levels)/len(levels),2) if levels else 0,"samples":len(levels)}}
