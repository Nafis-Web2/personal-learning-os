
from datetime import datetime,timedelta
from pydantic import BaseModel,Field
from sqlalchemy.orm import Session
from app.models import Concept,ConceptMastery,EvidenceEvent,MasteryHistory,ReviewSchedule,ReviewEvent,Misconception,RepairSession,DailyGate,DailyGateItem
from app.services.mastery import WEIGHTS

ALLOWED={'recall','understanding','application','transfer','independence','retention'}
HELP_CAP={0:100,1:95,2:85,3:75,4:60,5:40,6:0}
ASSESSMENT_MODES={'assessment','daily_gate','cold_test','weekly_synthesis'}

class EvidenceProposal(BaseModel):
    concept_id:str
    dimensions:dict[str,float]=Field(default_factory=dict)
    observable:bool=True
    correct:bool|None=None
    learner_confidence:str|None=None
    misconception:str|None=None
    rationale:str=''
    mode:str='teach'
    help_level:int=0

def validate_proposal(db:Session,user_id:str,p:EvidenceProposal):
    if not db.get(Concept,p.concept_id):return {'accepted':False,'reason':'concept_not_found'}
    if not p.observable:return {'accepted':False,'reason':'observable_performance_required'}
    effective_help=0 if p.mode in ASSESSMENT_MODES else max(0,min(6,p.help_level))
    if effective_help>=6:return {'accepted':False,'reason':'fresh_independent_retest_required','needs_retest':True}
    dims={k:max(0,min(100,float(v))) for k,v in p.dimensions.items() if k in ALLOWED}
    if not dims:return {'accepted':False,'reason':'no_valid_dimensions'}
    cap=HELP_CAP[effective_help]
    if 'independence' in dims:dims['independence']=min(dims['independence'],cap)
    # Heavy assistance cannot become strong evidence merely because the answer is correct.
    if effective_help>=4:
        for k in ('recall','understanding','application','transfer','retention'):
            if k in dims:dims[k]=min(dims[k],cap)
    return {'accepted':True,'dimensions':dims,'help_level':effective_help}

def _update_mastery(db,user_id,concept_id,dimension,score,help_level,rationale):
    db.add(EvidenceEvent(user_id=user_id,concept_id=concept_id,dimension=dimension,score=score,hint_level=help_level,source='ai_classroom_validated',rationale=rationale))
    m=db.query(ConceptMastery).filter_by(user_id=user_id,concept_id=concept_id).first()
    if not m:m=ConceptMastery(user_id=user_id,concept_id=concept_id);db.add(m);db.flush()
    old=float(getattr(m,dimension) or 0);new=round(old*.55+score*.45,2);setattr(m,dimension,new)
    m.overall=round(sum(float(getattr(m,k) or 0)*w for k,w in WEIGHTS.items()),2)
    db.flush();db.add(MasteryHistory(user_id=user_id,concept_id=concept_id,overall=m.overall,dimension=dimension,dimension_score=new))
    return m

def _review(db,user_id,concept_id,score):
    ladder=[1,3,7,14,30,60,120]
    r=db.query(ReviewSchedule).filter_by(user_id=user_id,concept_id=concept_id).first()
    if not r:r=ReviewSchedule(user_id=user_id,concept_id=concept_id,next_due_at=datetime.utcnow(),stage=0);db.add(r);db.flush()
    passed=score>=70;r.stage=min(r.stage+1,len(ladder)-1) if passed else max(r.stage-1,0)
    r.interval_days=ladder[r.stage];r.next_due_at=datetime.utcnow()+timedelta(days=r.interval_days);r.last_result='pass' if passed else 'fail'
    db.add(ReviewEvent(user_id=user_id,concept_id=concept_id,result=r.last_result,score=score))
    return r

def _misconception_and_repair(db,user_id,p):
    if p.correct is not False:return None
    desc=(p.misconception or p.rationale or 'Incorrect response requires targeted repair.').strip()
    m=Misconception(user_id=user_id,concept_id=p.concept_id,description=desc,confidence=p.learner_confidence)
    db.add(m)
    # Wrong + high confidence, or weak application/understanding, becomes repair priority.
    weak=min([float(v) for k,v in p.dimensions.items() if k in {'understanding','application'}] or [100])<70
    high=(p.learner_confidence or '').lower() in {'very_sure','high','very sure'}
    if weak or high:
        existing=db.query(RepairSession).filter_by(user_id=user_id,concept_id=p.concept_id,status='open').first()
        if not existing:
            existing=RepairSession(user_id=user_id,concept_id=p.concept_id,gap=desc,status='open');db.add(existing)
        return existing
    return None

def _apply_gate_result(db,user_id,p,aggregate_score):
    if p.mode!='daily_gate':return None
    item=(db.query(DailyGateItem).join(DailyGate,DailyGateItem.gate_id==DailyGate.id)
          .filter(DailyGate.user_id==user_id,DailyGate.status.in_(['pending','partial','fail']),DailyGateItem.concept_id==p.concept_id)
          .order_by(DailyGate.created_at.desc()).first())
    if not item:return None
    item.score=aggregate_score;item.result='pass' if aggregate_score>=70 else 'fail'
    gate=db.get(DailyGate,item.gate_id);items=db.query(DailyGateItem).filter_by(gate_id=gate.id).all()
    if all(x.score is not None for x in items):
        failures=sum((x.score or 0)<70 for x in items)
        gate.status='pass' if failures==0 else 'partial' if failures<len(items) else 'fail'
        gate.completed_at=datetime.utcnow()
    return gate

def apply_validated_proposal(db:Session,user_id:str,p:EvidenceProposal):
    v=validate_proposal(db,user_id,p)
    if not v['accepted']:return {**v,'mastery_updated':False}
    updated=None
    for dimension,score in v['dimensions'].items():
        updated=_update_mastery(db,user_id,p.concept_id,dimension,score,v['help_level'],p.rationale)
    aggregate=round(sum(v['dimensions'].values())/len(v['dimensions']),2)
    review=_review(db,user_id,p.concept_id,aggregate)
    repair=_misconception_and_repair(db,user_id,p)
    gate=_apply_gate_result(db,user_id,p,aggregate)
    db.commit()
    return {'accepted':True,'mastery_updated':True,'concept_id':p.concept_id,'dimensions':v['dimensions'],
      'overall':updated.overall if updated else None,'review_due_at':review.next_due_at.isoformat(),
      'repair_opened':bool(repair),'gate_status':getattr(gate,'status',None)}
