import os
os.environ['DATABASE_URL']='sqlite:///./test_learning_os.db'
from fastapi.testclient import TestClient
from app.main import app

def test_end_to_end_phase2():
    with TestClient(app) as c:
        u=c.post('/users',json={'display_name':'Test Learner'}).json(); uid=u['id']
        courses=c.get('/courses').json(); assert len(courses)>=2
        py=next(x for x in courses if x['code']=='PYTHON_FOUNDATIONS')
        e=c.post(f'/users/{uid}/enroll/{py["id"]}'); assert e.status_code==200
        ctx=c.get(f'/users/{uid}/continuity').json(); assert ctx['active_courses'][0]['course']=='Python Foundations'
        assert c.post(f'/users/{uid}/journal',json={'body':'private diary','entry_type':'personal'}).status_code==200
        ctx=c.get(f'/users/{uid}/continuity').json(); assert 'private diary' not in str(ctx)
        assert c.patch(f'/users/{uid}/privacy',json={'journal_ai_access':'full'}).status_code==200
        ctx=c.get(f'/users/{uid}/continuity').json(); assert 'private diary' in str(ctx)
        ex=c.get(f'/users/{uid}/export'); assert ex.status_code==200
        assert c.delete(f'/users/{uid}').status_code==200
        assert c.get(f'/users/{uid}/continuity').status_code==404
