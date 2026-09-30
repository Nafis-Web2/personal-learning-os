
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models import Course,Module,Lesson,Concept,ConceptPrerequisite,Enrollment
from app.services.curriculum_seed import seed_builtin_curriculum
from app.services.lesson_engine import start_course,active_concept

def test_builtin_python_and_trading_are_idempotent():
 db=SessionLocal()
 try:
  a=seed_builtin_curriculum(db);b=seed_builtin_curriculum(db)
  assert a['python'].id==b['python'].id and a['trading'].id==b['trading'].id
  assert db.query(Module).filter_by(course_id=a['python'].id).count()==14
  assert db.query(Module).filter_by(course_id=a['trading'].id).count()==13
  assert db.query(ConceptPrerequisite).count()>20
 finally:db.close()

def test_start_course_saves_real_lesson_and_concept():
 with TestClient(app) as c:
  uid=c.post('/users',json={'display_name':'Curriculum','timezone':'America/New_York'}).json()['id']
  db=SessionLocal()
  try:
   course=db.query(Course).filter_by(code='PYTHON-FOUNDATIONS').one()
   e=start_course(db,uid,course.id);concept=active_concept(db,uid,course.id)
   assert e.current_lesson_id and concept and concept.name=='running Python'
  finally:db.close()
