
import os
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models import TutorInteraction,JournalEntry,PrivacySetting
from app.services.teacher_context import build_teacher_context

def _user(c):
    return c.post('/users',json={'display_name':'Classroom Test','timezone':'America/New_York'}).json()['id']

def test_classroom_turn_persists_and_assessment_locks_help(monkeypatch):
    monkeypatch.setenv('AI_PROVIDER','mock')
    with TestClient(app) as c:
        uid=_user(c)
        r=c.post(f'/users/{uid}/teacher/classroom-turn',json={'message':'My explanation','mode':'assessment','help_level':5})
        assert r.status_code==200
        assert r.json()['help_level']==0
        db=SessionLocal()
        try:
            x=db.query(TutorInteraction).filter_by(user_id=uid).first()
            assert x and x.learner_input=='My explanation' and x.help_level==0
        finally:db.close()

def test_private_journal_never_enters_teacher_context():
    with TestClient(app) as c:
        uid=_user(c)
        db=SessionLocal()
        try:
            db.add(JournalEntry(user_id=uid,entry_type='personal',body='private text',tags=''))
            db.commit()
            assert build_teacher_context(db,uid)['authorized_journal_context']==[]
            p=db.get(PrivacySetting,uid);p.journal_ai_access='full';db.commit()
            assert 'private text' in build_teacher_context(db,uid)['authorized_journal_context']
        finally:db.close()
