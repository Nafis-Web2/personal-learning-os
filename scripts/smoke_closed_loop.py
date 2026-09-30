
import os,tempfile,sys,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
dbfile=os.path.join(tempfile.gettempdir(),'learning_os_closed_smoke.db')
try:os.remove(dbfile)
except FileNotFoundError:pass
os.environ['DATABASE_URL']='sqlite:///'+dbfile;os.environ['AI_PROVIDER']='mock'
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models import Course,Module,Lesson,Concept,EvidenceEvent,TutorInteraction
with TestClient(app) as c:
 uid=c.post('/users',json={'display_name':'Closed Smoke','timezone':'America/New_York'}).json()['id']
 db=SessionLocal();course=Course(code='Z'+uuid.uuid4().hex[:5],title='Course');db.add(course);db.flush();mod=Module(course_id=course.id,code='M',title='M',position=1);db.add(mod);db.flush();lesson=Lesson(module_id=mod.id,title='Loops',position=1);db.add(lesson);db.flush();concept=Concept(lesson_id=lesson.id,name='for loops',position=1);db.add(concept);db.commit();cid=concept.id;db.close()
 r=c.post(f'/users/{uid}/teacher/classroom-turn',json={'message':'A for loop repeats once for each item.','mode':'assessment','help_level':4,'concept_id':cid})
 assert r.status_code==200,r.text;j=r.json();assert j['help_level']==0
 assert j['evidence_result']['evaluated'] and not j['evidence_result']['accepted']
 db=SessionLocal()
 try:
  assert db.query(TutorInteraction).filter_by(user_id=uid).count()==1
  assert db.query(EvidenceEvent).filter_by(user_id=uid).count()==0
 finally:db.close()
print('Closed Classroom loop smoke test passed; offline evaluator failed closed with zero mastery writes.')
