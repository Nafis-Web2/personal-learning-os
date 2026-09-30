import os
os.environ['DATABASE_URL']='sqlite:///./test_learning_os.db'
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models import EvidenceEvent, ConceptMastery, ExternalLearningEvent, MediaUsageEvent

def test_phase3_persistence_and_no_fake_mastery():
    with TestClient(app) as c:
        uid=c.post('/users',json={'display_name':'Phase3 Learner'}).json()['id']
        before=SessionLocal()
        try:
            e0=before.query(EvidenceEvent).filter_by(user_id=uid).count(); m0=before.query(ConceptMastery).filter_by(user_id=uid).count()
        finally: before.close()
        x=c.post(f'/users/{uid}/external-learning',json={'source':'Zero to Mastery','topic':'Python functions','covered':'parameters, returns','minutes':55})
        assert x.status_code==200 and x.json()['status']=='awaiting_proof'
        cc=c.post(f'/users/{uid}/college-courses',json={'code':'MA440','title':'Precalculus','term':'Fall 2026'}); assert cc.status_code==200
        hw=c.post(f'/users/{uid}/homework',json={'college_course_id':cc.json()['id'],'title':'Logarithms HW'}); assert hw.status_code==200 and hw.json()['status']=='awaiting_analysis'
        r=c.post(f'/users/{uid}/resources',json={'title':'Functions visual','resource_type':'video','url':'https://example.invalid/video'}); assert r.status_code==200
        use=c.post(f'/users/{uid}/resources/{r.json()["id"]}/usage',json={'action':'viewed','seconds':120}); assert use.status_code==200 and use.json()['mastery_changed'] is False
        dash=c.get(f'/users/{uid}/dashboard').json(); assert dash['external_learning_pending'][0]['topic']=='Python functions'; assert dash['college_courses'][0]['code']=='MA440'; assert dash['assignments'][0]['title']=='Logarithms HW'
        after=SessionLocal()
        try:
            assert after.query(EvidenceEvent).filter_by(user_id=uid).count()==e0
            assert after.query(ConceptMastery).filter_by(user_id=uid).count()==m0
            assert after.query(ExternalLearningEvent).filter_by(user_id=uid).count()==1
            assert after.query(MediaUsageEvent).filter_by(user_id=uid).count()==1
        finally: after.close()
