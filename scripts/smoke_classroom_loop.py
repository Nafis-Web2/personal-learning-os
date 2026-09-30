
import os,tempfile,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
dbfile=os.path.join(tempfile.gettempdir(),'learning_os_classroom_smoke.db')
try:os.remove(dbfile)
except FileNotFoundError:pass
os.environ['DATABASE_URL']='sqlite:///'+dbfile
os.environ['AI_PROVIDER']='mock'
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models import TutorInteraction
with TestClient(app) as c:
    u=c.post('/users',json={'display_name':'Classroom Smoke','timezone':'America/New_York'})
    assert u.status_code==200,u.text;uid=u.json()['id']
    r=c.post(f'/users/{uid}/teacher/classroom-turn',json={'message':'I think loops repeat instructions.','mode':'teach','help_level':0})
    assert r.status_code==200,r.text
    j=r.json();assert j['provider']=='mock' and j['interaction_id'] and 'next_action' in j
    a=c.post(f'/users/{uid}/teacher/classroom-turn',json={'message':'Testing myself','mode':'cold_test','help_level':5})
    assert a.status_code==200 and a.json()['help_level']==0
    db=SessionLocal()
    try: assert db.query(TutorInteraction).filter_by(user_id=uid).count()==2
    finally:db.close()
print('Persistent Classroom AI loop smoke test passed.')
