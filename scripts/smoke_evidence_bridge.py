
import os,tempfile,sys,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
dbfile=os.path.join(tempfile.gettempdir(),'learning_os_evidence_smoke.db')
try:os.remove(dbfile)
except FileNotFoundError:pass
os.environ['DATABASE_URL']='sqlite:///'+dbfile
os.environ['AI_PROVIDER']='mock'
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models import Course,Module,Lesson,Concept,DailyGate,DailyGateItem,ConceptMastery,EvidenceEvent,ReviewSchedule
with TestClient(app) as c:
 u=c.post('/users',json={'display_name':'Evidence Smoke','timezone':'America/New_York'});assert u.status_code==200;uid=u.json()['id']
 db=SessionLocal()
 course=Course(code='SMOKE-'+uuid.uuid4().hex[:5],title='Smoke Course');db.add(course);db.flush()
 mod=Module(course_id=course.id,code='M1',title='Basics',position=1);db.add(mod);db.flush()
 lesson=Lesson(module_id=mod.id,title='Loops',position=1);db.add(lesson);db.flush()
 concept=Concept(lesson_id=lesson.id,name='for loops',position=1);db.add(concept);db.flush()
 gate=DailyGate(user_id=uid,course_id=course.id,status='pending');db.add(gate);db.flush()
 item=DailyGateItem(gate_id=gate.id,concept_id=concept.id);db.add(item);db.commit();cid=concept.id;gid=gate.id;db.close()
 r=c.post(f'/users/{uid}/teacher/evidence',json={'concept_id':cid,'dimensions':{'recall':88,'understanding':84,'application':82,'independence':95},'observable':True,'correct':True,'mode':'daily_gate','help_level':5,'rationale':'Independent explanation and fresh application.'})
 assert r.status_code==200,r.text;j=r.json();assert j['accepted'] and j['mastery_updated'] and j['gate_status']=='pass'
 db=SessionLocal()
 try:
  assert db.query(EvidenceEvent).filter_by(user_id=uid,concept_id=cid).count()==4
  assert db.query(ConceptMastery).filter_by(user_id=uid,concept_id=cid).first() is not None
  assert db.query(ReviewSchedule).filter_by(user_id=uid,concept_id=cid).first() is not None
  assert db.get(DailyGate,gid).status=='pass'
 finally:db.close()
print('Evidence → mastery → review → Daily Gate smoke test passed.')
