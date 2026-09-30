
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models import Course,Module,Lesson,Concept,ConceptMastery,RepairSession,EvidenceEvent
from app.services.evidence_pipeline import EvidenceProposal,apply_validated_proposal

def seeded(db):
 c=Course(code='EV-'+__import__('uuid').uuid4().hex[:6],title='Evidence');db.add(c);db.flush()
 m=Module(course_id=c.id,code='M1',title='M',position=1);db.add(m);db.flush()
 l=Lesson(module_id=m.id,title='L',position=1);db.add(l);db.flush()
 x=Concept(lesson_id=l.id,name='Loops',position=1);db.add(x);db.commit();return x

def user(c):return c.post('/users',json={'display_name':'Evidence Test','timezone':'America/New_York'}).json()['id']

def test_unobservable_never_updates_mastery():
 with TestClient(app) as c:
  uid=user(c);db=SessionLocal()
  try:
   x=seeded(db);r=apply_validated_proposal(db,uid,EvidenceProposal(concept_id=x.id,dimensions={'understanding':95},observable=False))
   assert not r['accepted'] and db.query(EvidenceEvent).filter_by(user_id=uid).count()==0
  finally:db.close()

def test_full_solution_requires_fresh_retest():
 with TestClient(app) as c:
  uid=user(c);db=SessionLocal()
  try:
   x=seeded(db);r=apply_validated_proposal(db,uid,EvidenceProposal(concept_id=x.id,dimensions={'application':100},help_level=6))
   assert r['needs_retest'] and db.query(ConceptMastery).filter_by(user_id=uid,concept_id=x.id).first() is None
  finally:db.close()

def test_wrong_high_confidence_opens_repair():
 with TestClient(app) as c:
  uid=user(c);db=SessionLocal()
  try:
   x=seeded(db);r=apply_validated_proposal(db,uid,EvidenceProposal(concept_id=x.id,dimensions={'understanding':35,'application':30},correct=False,learner_confidence='very_sure',misconception='A loop always runs forever.'))
   assert r['accepted'] and r['repair_opened']
   assert db.query(RepairSession).filter_by(user_id=uid,concept_id=x.id,status='open').first()
  finally:db.close()

def test_assessment_ignores_requested_help():
 with TestClient(app) as c:
  uid=user(c);db=SessionLocal()
  try:
   x=seeded(db);r=apply_validated_proposal(db,uid,EvidenceProposal(concept_id=x.id,dimensions={'independence':90},mode='cold_test',help_level=5))
   assert r['dimensions']['independence']==90
  finally:db.close()
