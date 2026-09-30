from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Enrollment, Course, Lesson, ConceptMastery, ReviewSchedule, SessionSummary, PrivacySetting, JournalEntry, LearningLog

def build_context(db: Session, user_id: str):
    enrollments = db.query(Enrollment).filter_by(user_id=user_id, active=True).all()
    courses=[]
    for e in enrollments:
        c=db.get(Course,e.course_id); l=db.get(Lesson,e.current_lesson_id) if e.current_lesson_id else None
        courses.append({"course_id":c.id,"course":c.title,"current_lesson":l.title if l else None})
    mastery=db.query(ConceptMastery).filter_by(user_id=user_id).all()
    due=db.query(ReviewSchedule).filter(ReviewSchedule.user_id==user_id, ReviewSchedule.next_due_at<=datetime.utcnow()).all()
    last=db.query(SessionSummary).filter_by(user_id=user_id).order_by(SessionSummary.created_at.desc()).first()
    privacy=db.get(PrivacySetting,user_id)
    journal=[]
    if privacy and privacy.journal_ai_access=="full":
        journal=[j.body for j in db.query(JournalEntry).filter_by(user_id=user_id).order_by(JournalEntry.created_at.desc()).limit(5)]
    elif privacy and privacy.journal_ai_access=="learning_only":
        journal=[j.body for j in db.query(JournalEntry).filter_by(user_id=user_id,entry_type="learning").order_by(JournalEntry.created_at.desc()).limit(5)]
    logs=[x.body for x in db.query(LearningLog).filter_by(user_id=user_id).order_by(LearningLog.created_at.desc()).limit(5)]
    return {"active_courses":courses,"last_session": None if not last else {"summary":last.summary,"unresolved_gaps":last.unresolved_gaps,"next_step":last.next_step},"mastery":[{"concept_id":m.concept_id,"overall":m.overall,"understanding":m.understanding,"application":m.application,"retention":m.retention} for m in mastery],"reviews_due":[{"concept_id":r.concept_id,"due":r.next_due_at.isoformat()} for r in due],"learning_logs":logs,"authorized_journal_context":journal}
