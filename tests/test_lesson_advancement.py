
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models import Course,ConceptMastery,Concept,Lesson,Module
from app.services.lesson_engine import start_course,active_concept,advance_position

def test_cannot_advance_without_mastery():
 with TestClient(app) as c:
  uid=c.post('/users',json={'display_name':'Advance','timezone':'America/New_York'}).json()['id'];db=SessionLocal()
  try:
   course=db.query(Course).filter_by(code='PYTHON-FOUNDATIONS').one();start_course(db,uid,course.id)
   r=advance_position(db,uid,course.id)
   assert not r['advanced'] and r['reason']=='mastery_not_ready'
  finally:db.close()

def test_mastered_lesson_advances_saved_position():
 with TestClient(app) as c:
  uid=c.post('/users',json={'display_name':'Advance2','timezone':'America/New_York'}).json()['id'];db=SessionLocal()
  try:
   course=db.query(Course).filter_by(code='PYTHON-FOUNDATIONS').one();e=start_course(db,uid,course.id)
   first=e.current_lesson_id
   concepts=db.query(Concept).filter_by(lesson_id=first).all()
   for x in concepts:db.add(ConceptMastery(user_id=uid,concept_id=x.id,overall=85,understanding=80,application=80,recall=85,transfer=70,independence=80,retention=75))
   db.commit();r=advance_position(db,uid,course.id)
   assert r['advanced'] and r['lesson']['id']!=first
  finally:db.close()
