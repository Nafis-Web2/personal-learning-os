
import os,tempfile,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
dbfile=os.path.join(tempfile.gettempdir(),'learning_os_curriculum_smoke.db')
try:os.remove(dbfile)
except FileNotFoundError:pass
os.environ['DATABASE_URL']='sqlite:///'+dbfile;os.environ['AI_PROVIDER']='mock'
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models import Course,TutorInteraction
with TestClient(app) as c:
 courses=c.get('/curriculum');assert courses.status_code==200
 data=courses.json();assert {x['code'] for x in data}=={'PYTHON-FOUNDATIONS','TRADING-FOUNDATIONS'}
 py=next(x for x in data if x['code']=='PYTHON-FOUNDATIONS')
 assert len(py['modules'])==14
 uid=c.post('/users',json={'display_name':'Learner','timezone':'America/New_York'}).json()['id']
 st=c.post(f"/users/{uid}/courses/{py['id']}/start");assert st.status_code==200,st.text
 assert st.json()['active_concept']['name']=='running Python'
 turn=c.post(f"/users/{uid}/teacher/classroom-turn",json={'message':'I run Python files from my environment.','mode':'teach','help_level':0,'course_id':py['id']})
 assert turn.status_code==200,turn.text
 db=SessionLocal()
 try:
  interaction=db.query(TutorInteraction).filter_by(user_id=uid).first()
  assert interaction and interaction.concept_id==st.json()['active_concept']['id']
 finally:db.close()
print('Curriculum → Start Learning → explicit concept Classroom smoke test passed.')
