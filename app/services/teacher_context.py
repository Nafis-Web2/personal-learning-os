
import json
from datetime import datetime
from app.models import Enrollment,Course,Lesson,Module,Concept,ConceptMastery,ReviewSchedule,Misconception,TutorInteraction,PrivacySetting,JournalEntry

def build_teacher_context(db,user_id:str,course_id:str|None=None):
    enrollments=db.query(Enrollment).filter_by(user_id=user_id,active=True).all()
    active=next((e for e in enrollments if e.course_id==course_id),enrollments[0] if enrollments else None)
    course=db.get(Course,active.course_id) if active else None
    lesson=db.get(Lesson,active.current_lesson_id) if active and active.current_lesson_id else None
    module=db.get(Module,lesson.module_id) if lesson else None
    concepts=db.query(Concept).filter_by(lesson_id=lesson.id).order_by(Concept.position).all() if lesson else []
    concept_ids=[c.id for c in concepts]
    mastery=db.query(ConceptMastery).filter(ConceptMastery.user_id==user_id,ConceptMastery.concept_id.in_(concept_ids)).all() if concept_ids else []
    due=db.query(ReviewSchedule).filter(ReviewSchedule.user_id==user_id,ReviewSchedule.next_due_at<=datetime.utcnow()).order_by(ReviewSchedule.next_due_at).limit(5).all()
    misc=db.query(Misconception).filter_by(user_id=user_id,resolved=False).order_by(Misconception.first_seen_at.desc()).limit(5).all()
    recent=db.query(TutorInteraction).filter_by(user_id=user_id).order_by(TutorInteraction.created_at.desc()).limit(6).all()
    privacy=db.get(PrivacySetting,user_id);journal=[]
    if privacy and privacy.journal_ai_access=='full':
        journal=[j.body for j in db.query(JournalEntry).filter_by(user_id=user_id).order_by(JournalEntry.created_at.desc()).limit(3)]
    elif privacy and privacy.journal_ai_access=='learning_only':
        journal=[j.body for j in db.query(JournalEntry).filter_by(user_id=user_id,entry_type='learning').order_by(JournalEntry.created_at.desc()).limit(3)]
    return {
      'course':None if not course else {'id':course.id,'code':course.code,'title':course.title},
      'position':None if not lesson else {'module':getattr(module,'title',None),'lesson_id':lesson.id,'lesson':lesson.title},
      'lesson_concepts':[{'id':c.id,'name':c.name} for c in concepts],
      'mastery':[{'concept_id':m.concept_id,'overall':m.overall,'understanding':m.understanding,'application':m.application,'retention':m.retention,'independence':m.independence} for m in mastery],
      'reviews_due':[{'concept_id':r.concept_id,'due':r.next_due_at.isoformat()} for r in due],
      'misconceptions':[{'concept_id':m.concept_id,'description':m.description,'confidence':m.confidence} for m in misc],
      'recent_tutor_turns':[{'mode':x.mode,'learner':x.learner_input[-800:],'tutor':x.tutor_output[-1200:]} for x in reversed(recent)],
      'authorized_journal_context':journal,
    }

def compact_teacher_context(ctx:dict)->str:
    return json.dumps(ctx,ensure_ascii=False,separators=(',',':'))
