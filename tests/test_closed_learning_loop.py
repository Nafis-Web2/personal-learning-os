
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models import Course,Module,Lesson,Concept,ConceptMastery,EvidenceEvent
from app.services.ai_evaluator import EvaluationOutput
import app.services.ai_evaluator as ae
import uuid

class GoodEvaluator:
 def evaluate(self,**kwargs):
  return EvaluationOutput(should_record=True,concept_id=kwargs['concept_id'],dimensions={'understanding':90,'application':85,'independence':95},observable=True,correct=True,rationale='Explained mechanism and applied it.')

class BadConceptEvaluator:
 def evaluate(self,**kwargs):
  return EvaluationOutput(should_record=True,concept_id='wrong-id',dimensions={'understanding':100},observable=True,correct=True)

def seed(db):
 c=Course(code='CL-'+uuid.uuid4().hex[:6],title='Closed Loop');db.add(c);db.flush();m=Module(course_id=c.id,code='M',title='M',position=1);db.add(m);db.flush();l=Lesson(module_id=m.id,title='Loops',position=1);db.add(l);db.flush();x=Concept(lesson_id=l.id,name='for loops',position=1);db.add(x);db.commit();return x

def test_evaluator_can_propose_but_validator_updates(monkeypatch):
 with TestClient(app) as c:
  uid=c.post('/users',json={'display_name':'Closed','timezone':'America/New_York'}).json()['id'];db=SessionLocal()
  try:
   x=seed(db);monkeypatch.setattr(ae,'get_evaluator',lambda:GoodEvaluator())
   r=ae.evaluate_and_apply(db,uid,learner_input='A for loop iterates over each item; for x in [1,2] runs twice.',concept_id=x.id,mode='assessment',help_level=0,topic='for loops')
   assert r['accepted'] and r['mastery_updated']
   assert db.query(EvidenceEvent).filter_by(user_id=uid,concept_id=x.id).count()==3
  finally:db.close()

def test_concept_mismatch_fails_closed(monkeypatch):
 with TestClient(app) as c:
  uid=c.post('/users',json={'display_name':'Closed2','timezone':'America/New_York'}).json()['id'];db=SessionLocal()
  try:
   x=seed(db);monkeypatch.setattr(ae,'get_evaluator',lambda:BadConceptEvaluator())
   r=ae.evaluate_and_apply(db,uid,learner_input='answer',concept_id=x.id,mode='teach',help_level=0,topic='for loops')
   assert not r['accepted'] and r['reason']=='concept_identity_mismatch'
   assert db.query(EvidenceEvent).filter_by(user_id=uid).count()==0
  finally:db.close()

def test_mock_evaluator_does_not_invent_mastery(monkeypatch):
 monkeypatch.setattr(ae,'get_evaluator',lambda:ae.MockEvaluator())
 with TestClient(app) as c:
  uid=c.post('/users',json={'display_name':'Closed3','timezone':'America/New_York'}).json()['id'];db=SessionLocal()
  try:
   x=seed(db);r=ae.evaluate_and_apply(db,uid,learner_input='some answer',concept_id=x.id,mode='teach',help_level=0,topic='loops')
   assert not r['accepted'] and not r['mastery_updated']
  finally:db.close()
