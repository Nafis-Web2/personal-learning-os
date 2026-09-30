from datetime import datetime,timedelta
from sqlalchemy.orm import Session
from app.models import ReviewSchedule,ReviewEvent
INTERVALS=[1,3,7,14,30,60,120]
def update_review(db:Session,user_id:str,concept_id:str,score:float):
    row=db.query(ReviewSchedule).filter_by(user_id=user_id,concept_id=concept_id).first()
    if not row: row=ReviewSchedule(user_id=user_id,concept_id=concept_id,next_due_at=datetime.utcnow(),stage=0); db.add(row)
    result='pass' if score>=70 else 'fail'
    row.stage=min((row.stage+1 if result=='pass' else max(row.stage-1,0)),len(INTERVALS)-1)
    row.interval_days=INTERVALS[row.stage]; row.next_due_at=datetime.utcnow()+timedelta(days=row.interval_days); row.last_result=result
    db.add(ReviewEvent(user_id=user_id,concept_id=concept_id,result=result,score=score)); db.commit(); db.refresh(row); return row
