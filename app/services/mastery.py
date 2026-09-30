from sqlalchemy.orm import Session
from app.models import ConceptMastery,EvidenceEvent,MasteryHistory,Concept
WEIGHTS={'recall':.20,'understanding':.20,'application':.25,'transfer':.15,'independence':.10,'retention':.10}
def record_evidence(db:Session,user_id:str,data):
    if not db.get(Concept,data.concept_id): raise ValueError('Concept not found')
    db.add(EvidenceEvent(user_id=user_id,**data.model_dump()))
    m=db.query(ConceptMastery).filter_by(user_id=user_id,concept_id=data.concept_id).first()
    if not m: m=ConceptMastery(user_id=user_id,concept_id=data.concept_id); db.add(m)
    adjusted=data.score*max(.25,1-data.hint_level*.12); old=getattr(m,data.dimension); new=round(old*.55+adjusted*.45,2); setattr(m,data.dimension,new)
    m.overall=round(sum(getattr(m,k)*w for k,w in WEIGHTS.items()),2); db.flush()
    db.add(MasteryHistory(user_id=user_id,concept_id=data.concept_id,overall=m.overall,dimension=data.dimension,dimension_score=new)); db.commit(); db.refresh(m); return m
