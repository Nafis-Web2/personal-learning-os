
import os,tempfile,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
dbfile=os.path.join(tempfile.gettempdir(),'learning_os_learner_flow.db')
try:os.remove(dbfile)
except FileNotFoundError:pass
os.environ['DATABASE_URL']='sqlite:///'+dbfile;os.environ['AI_PROVIDER']='mock'
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models import ConceptMastery,Concept
with TestClient(app) as c:
 curriculum=c.get('/curriculum').json();py=next(x for x in curriculum if x['code']=='PYTHON-FOUNDATIONS')
 uid=c.post('/users',json={'display_name':'UI Learner','timezone':'America/New_York'}).json()['id']
 start=c.post(f"/users/{uid}/courses/{py['id']}/start");assert start.status_code==200
 cid=start.json()['active_concept']['id']
 pos=c.get(f"/users/{uid}/courses/{py['id']}/position");assert pos.status_code==200 and pos.json()['active_concept']['id']==cid
 blocked=c.post(f"/users/{uid}/courses/{py['id']}/advance");assert blocked.status_code==200 and blocked.json()['reason']=='mastery_not_ready'
 db=SessionLocal();concepts=db.query(Concept).filter_by(lesson_id=start.json()['lesson_id']).all()
 for x in concepts:db.add(ConceptMastery(user_id=uid,concept_id=x.id,overall=85,understanding=80,application=80,recall=80,transfer=75,independence=80,retention=75))
 db.commit();db.close()
 advanced=c.post(f"/users/{uid}/courses/{py['id']}/advance");assert advanced.status_code==200 and advanced.json()['advanced']
 newpos=c.get(f"/users/{uid}/courses/{py['id']}/position").json();assert newpos['lesson']['id']==advanced.json()['lesson']['id']
print('Today/Roadmap → Start → mastery gate → lesson advancement smoke test passed.')
