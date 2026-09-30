from datetime import datetime
from fastapi import FastAPI,Depends,HTTPException,UploadFile,File,Form,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import allowed_origins,is_production
from sqlalchemy.orm import Session
from app.db.base import Base
from app.db.session import engine,get_db
from app.models import *
from app.schemas.api import *
from app.services.mastery import record_evidence
from app.services.reviews import update_review
from app.services.continuity import build_context
from app.seed.curricula import seed_all
from app.services.supabase_auth import verify_supabase_token
app=FastAPI(title='Personal Learning OS API',version='0.3.0')
app.add_middleware(CORSMiddleware,allow_origins=allowed_origins(),allow_credentials=True,allow_methods=['*'],allow_headers=['*'])

@app.middleware('http')
async def protect_user_routes(request:Request,call_next):
    if request.method=='OPTIONS':
        return await call_next(request)
    path=request.url.path
    if is_production() and path.startswith('/users/'):
        auth=request.headers.get('authorization','')
        if not auth.lower().startswith('bearer '):
            return JSONResponse({'detail':'Authentication required'},status_code=401)
        try:
            claims=verify_supabase_token(auth.split(' ',1)[1])
        except HTTPException as e:
            return JSONResponse({'detail':e.detail},status_code=e.status_code)
        provider_subject=claims.get('id') or claims.get('sub')
        from app.db.session import SessionLocal
        db=SessionLocal()
        try:
            ident=db.query(AuthIdentity).filter_by(provider='supabase',provider_subject=provider_subject).first()
            requested=path.split('/')[2] if len(path.split('/'))>2 else ''
            if not ident or ident.user_id!=requested:
                return JSONResponse({'detail':'Forbidden'},status_code=403)
        finally:
            db.close()
    return await call_next(request)

@app.on_event('startup')
def startup():
    Base.metadata.create_all(bind=engine)
    from app.db.session import SessionLocal
    db=SessionLocal()
    try: seed_all(db)
    finally: db.close()
@app.get('/health')
def health(): return {'status':'ok','phase':3}

@app.get('/auth/me')
def auth_me(request:Request,db:Session=Depends(get_db)):
    auth=request.headers.get('authorization','')
    if not auth.lower().startswith('bearer '): raise HTTPException(401,'Authentication required')
    claims=verify_supabase_token(auth.split(' ',1)[1])
    subject=claims.get('id') or claims.get('sub')
    ident=db.query(AuthIdentity).filter_by(provider='supabase',provider_subject=subject).first()
    if ident:
        u=db.get(User,ident.user_id)
    else:
        meta=claims.get('user_metadata') or {}
        email=claims.get('email') or ''
        display=meta.get('full_name') or meta.get('name') or (email.split('@')[0] if email else 'Learner')
        u=User(display_name=display,timezone='America/New_York');db.add(u);db.flush()
        db.add(AuthIdentity(user_id=u.id,provider='supabase',provider_subject=subject))
        db.add(PrivacySetting(user_id=u.id));db.commit();db.refresh(u)
    return {'id':u.id,'display_name':u.display_name,'timezone':u.timezone,'email':claims.get('email')}
@app.post('/users')
def create_user(data:UserCreate,db:Session=Depends(get_db)):
    u=User(**data.model_dump()); db.add(u); db.flush(); db.add(PrivacySetting(user_id=u.id)); db.commit(); db.refresh(u); return {'id':u.id,'display_name':u.display_name,'timezone':u.timezone}
@app.get('/courses')
def courses(db:Session=Depends(get_db)): return [{'id':c.id,'code':c.code,'title':c.title,'version':c.version} for c in db.query(Course).all()]
@app.post('/users/{user_id}/enroll/{course_id}')
def enroll(user_id:str,course_id:str,db:Session=Depends(get_db)):
    if not db.get(User,user_id) or not db.get(Course,course_id): raise HTTPException(404,'User or course not found')
    e=db.query(Enrollment).filter_by(user_id=user_id,course_id=course_id).first()
    if e:return {'id':e.id,'status':'already_enrolled','current_lesson_id':e.current_lesson_id}
    m=db.query(Module).filter_by(course_id=course_id).order_by(Module.position).first(); l=db.query(Lesson).filter_by(module_id=m.id).order_by(Lesson.position).first() if m else None
    e=Enrollment(user_id=user_id,course_id=course_id,current_lesson_id=l.id if l else None);db.add(e);db.commit();db.refresh(e);return {'id':e.id,'current_lesson_id':e.current_lesson_id}
@app.post('/users/{user_id}/journal')
def journal(user_id:str,data:JournalCreate,db:Session=Depends(get_db)):
    if not db.get(User,user_id): raise HTTPException(404,'User not found')
    if data.entry_type not in {'personal','learning'}: raise HTTPException(400,'Invalid entry type')
    j=JournalEntry(user_id=user_id,body=data.body,entry_type=data.entry_type,tags=','.join(data.tags));db.add(j);db.commit();db.refresh(j);return {'id':j.id,'created_at':j.created_at}
@app.patch('/users/{user_id}/privacy')
def privacy(user_id:str,data:PrivacyUpdate,db:Session=Depends(get_db)):
    if data.journal_ai_access not in {'private','learning_only','full'}: raise HTTPException(400,'Invalid journal access mode')
    p=db.get(PrivacySetting,user_id); 
    if not p: raise HTTPException(404,'User not found')
    p.journal_ai_access=data.journal_ai_access;db.commit();return {'journal_ai_access':p.journal_ai_access}
@app.post('/users/{user_id}/evidence')
def evidence(user_id:str,data:EvidenceCreate,db:Session=Depends(get_db)):
    if not db.get(User,user_id): raise HTTPException(404,'User not found')
    if data.dimension not in {'recall','understanding','application','transfer','independence','retention'}: raise HTTPException(400,'Invalid mastery dimension')
    try:m=record_evidence(db,user_id,data)
    except ValueError as e: raise HTTPException(404,str(e))
    return {'concept_id':m.concept_id,'overall':m.overall,'understanding':m.understanding,'application':m.application,'retention':m.retention}
@app.post('/users/{user_id}/reviews')
def review(user_id:str,data:ReviewCreate,db:Session=Depends(get_db)):
    if not db.get(User,user_id) or not db.get(Concept,data.concept_id): raise HTTPException(404,'User or concept not found')
    r=update_review(db,user_id,data.concept_id,data.score);return {'next_due_at':r.next_due_at,'interval_days':r.interval_days,'last_result':r.last_result}
@app.post('/users/{user_id}/gates')
def create_gate(user_id:str,data:GateCreate,db:Session=Depends(get_db)):
    if not db.get(User,user_id) or not db.get(Course,data.course_id): raise HTTPException(404,'User or course not found')
    g=DailyGate(user_id=user_id,course_id=data.course_id);db.add(g);db.flush()
    for cid in data.concept_ids:
        if not db.get(Concept,cid): raise HTTPException(404,f'Concept {cid} not found')
        db.add(DailyGateItem(gate_id=g.id,concept_id=cid))
    db.commit();return {'id':g.id,'status':g.status}
@app.patch('/users/{user_id}/gates/{gate_id}')
def complete_gate(user_id:str,gate_id:str,data:GateComplete,db:Session=Depends(get_db)):
    if data.status not in {'pass','partial','fail'}: raise HTTPException(400,'Invalid gate status')
    g=db.query(DailyGate).filter_by(id=gate_id,user_id=user_id).first()
    if not g: raise HTTPException(404,'Gate not found')
    g.status=data.status;g.summary=data.summary;g.completed_at=datetime.utcnow();db.commit();return {'id':g.id,'status':g.status}
@app.post('/users/{user_id}/misconceptions')
def misconception(user_id:str,data:MisconceptionCreate,db:Session=Depends(get_db)):
    if not db.get(User,user_id) or not db.get(Concept,data.concept_id): raise HTTPException(404,'User or concept not found')
    m=Misconception(user_id=user_id,**data.model_dump());db.add(m);db.commit();db.refresh(m);return {'id':m.id,'resolved':m.resolved}
@app.patch('/users/{user_id}/misconceptions/{mid}/resolve')
def resolve_misconception(user_id:str,mid:str,db:Session=Depends(get_db)):
    m=db.query(Misconception).filter_by(id=mid,user_id=user_id).first()
    if not m: raise HTTPException(404,'Misconception not found')
    m.resolved=True;m.resolved_at=datetime.utcnow();db.commit();return {'id':m.id,'resolved':True}
@app.post('/users/{user_id}/files')
def file_meta(user_id:str,data:FileMetaCreate,db:Session=Depends(get_db)):
    if not db.get(User,user_id): raise HTTPException(404,'User not found')
    f=FileRecord(user_id=user_id,filename=data.filename,storage_key=data.storage_key,mime_type=data.mime_type,size_bytes=data.size_bytes,checksum=data.checksum);db.add(f);db.flush()
    if data.course_id:
        if not db.get(Course,data.course_id): raise HTTPException(404,'Course not found')
        db.add(FileCourseLink(file_id=f.id,course_id=data.course_id))
    db.commit();return {'id':f.id,'filename':f.filename}
@app.get('/users/{user_id}/continuity')
def continuity(user_id:str,db:Session=Depends(get_db)):
    if not db.get(User,user_id): raise HTTPException(404,'User not found')
    return build_context(db,user_id)
@app.get('/users/{user_id}/export')
def export_user(user_id:str,db:Session=Depends(get_db)):
    u=db.get(User,user_id)
    if not u: raise HTTPException(404,'User not found')
    return {'profile':{'id':u.id,'display_name':u.display_name,'timezone':u.timezone,'created_at':u.created_at},'continuity':build_context(db,user_id),'journal':[{'type':j.entry_type,'body':j.body,'tags':j.tags,'created_at':j.created_at} for j in db.query(JournalEntry).filter_by(user_id=user_id).all()],'evidence':[{'concept_id':e.concept_id,'dimension':e.dimension,'score':e.score,'hint_level':e.hint_level,'source':e.source,'created_at':e.created_at} for e in db.query(EvidenceEvent).filter_by(user_id=user_id).all()]}
@app.delete('/users/{user_id}')
def delete_user(user_id:str,db:Session=Depends(get_db)):
    if not db.get(User,user_id): raise HTTPException(404,'User not found')
    # Explicit user-owned deletion keeps shared curriculum intact.
    for model in [FileCourseLink]:
        ids=[x.id for x in db.query(FileRecord).filter_by(user_id=user_id).all()]
        if ids: db.query(model).filter(model.file_id.in_(ids)).delete(synchronize_session=False)
    for model in [DailyGateItem]:
        gids=[x.id for x in db.query(DailyGate).filter_by(user_id=user_id).all()]
        if gids: db.query(model).filter(model.gate_id.in_(gids)).delete(synchronize_session=False)
    for model in [AuthIdentity,PrivacySetting,Enrollment,LessonProgress,ConceptMastery,MasteryHistory,EvidenceEvent,Misconception,ReviewSchedule,ReviewEvent,RepairSession,HelpEvent,StudySession,SessionSummary,JournalEntry,LearningLog,FileRecord,DailyGate]: db.query(model).filter_by(user_id=user_id).delete(synchronize_session=False)
    db.delete(db.get(User,user_id));db.commit();return {'deleted':True}

# --- Phase 3 endpoints ---
@app.get('/users/{user_id}/dashboard')
def dashboard(user_id:str,db:Session=Depends(get_db)):
    if not db.get(User,user_id): raise HTTPException(404,'User not found')
    ext=db.query(ExternalLearningEvent).filter_by(user_id=user_id,status='awaiting_proof').order_by(ExternalLearningEvent.created_at.desc()).all()
    college=db.query(CollegeCourse).filter_by(user_id=user_id,active=True).all()
    hw=db.query(Assignment).filter(Assignment.user_id==user_id,Assignment.status!='complete').order_by(Assignment.due_at.asc()).all()
    ctx=build_context(db,user_id)
    return {'daily_gate':None,'reviews_due':ctx.get('reviews_due',[]),'active_courses':ctx.get('active_courses',[]),'external_learning_pending':[{'id':x.id,'source':x.source,'topic':x.topic,'status':x.status} for x in ext],'college_courses':[{'id':x.id,'code':x.code,'title':x.title,'term':x.term} for x in college],'assignments':[{'id':x.id,'title':x.title,'status':x.status,'due_at':x.due_at} for x in hw]}

@app.post('/users/{user_id}/external-learning')
def external_learning(user_id:str,data:ExternalLearningCreate,db:Session=Depends(get_db)):
    if not db.get(User,user_id): raise HTTPException(404,'User not found')
    x=ExternalLearningEvent(user_id=user_id,**data.model_dump()); db.add(x); db.commit(); db.refresh(x)
    return {'id':x.id,'status':x.status,'next_action':'proof_session'}

@app.post('/users/{user_id}/college-courses')
def add_college_course(user_id:str,data:CollegeCourseCreate,db:Session=Depends(get_db)):
    if not db.get(User,user_id): raise HTTPException(404,'User not found')
    x=CollegeCourse(user_id=user_id,**data.model_dump()); db.add(x); db.commit(); db.refresh(x)
    return {'id':x.id,'code':x.code,'title':x.title,'term':x.term}

@app.get('/users/{user_id}/college-courses')
def list_college_courses(user_id:str,db:Session=Depends(get_db)):
    if not db.get(User,user_id): raise HTTPException(404,'User not found')
    return [{'id':x.id,'code':x.code,'title':x.title,'term':x.term,'active':x.active} for x in db.query(CollegeCourse).filter_by(user_id=user_id).all()]

@app.post('/users/{user_id}/homework')
def add_homework(user_id:str,data:HomeworkCreate,db:Session=Depends(get_db)):
    if not db.get(User,user_id): raise HTTPException(404,'User not found')
    if data.college_course_id:
        cc=db.query(CollegeCourse).filter_by(id=data.college_course_id,user_id=user_id).first()
        if not cc: raise HTTPException(404,'College course not found')
    x=Assignment(user_id=user_id,**data.model_dump()); db.add(x); db.commit(); db.refresh(x)
    return {'id':x.id,'status':x.status,'pipeline':['analyze','diagnose','attempt','hint','fresh_check']}

@app.post('/users/{user_id}/resources')
def add_resource(user_id:str,data:ResourceCreate,db:Session=Depends(get_db)):
    if not db.get(User,user_id): raise HTTPException(404,'User not found')
    if data.resource_type not in {'video','diagram','graph','article','interactive','file'}: raise HTTPException(400,'Invalid resource type')
    if data.file_id:
        f=db.query(FileRecord).filter_by(id=data.file_id,user_id=user_id).first()
        if not f: raise HTTPException(404,'File not found')
    x=LearningResource(user_id=user_id,**data.model_dump()); db.add(x); db.commit(); db.refresh(x); return {'id':x.id,'resource_type':x.resource_type}

@app.post('/users/{user_id}/resources/{resource_id}/usage')
def media_usage(user_id:str,resource_id:str,data:MediaUsageCreate,db:Session=Depends(get_db)):
    r=db.query(LearningResource).filter_by(id=resource_id,user_id=user_id).first()
    if not r: raise HTTPException(404,'Resource not found')
    x=MediaUsageEvent(user_id=user_id,resource_id=resource_id,**data.model_dump()); db.add(x); db.commit(); db.refresh(x)
    return {'id':x.id,'recorded':True,'mastery_changed':False}


# --- Phase 3 consolidated read views / uploads ---
from app.services.storage import storage,ALLOWED,MAX_BYTES
from app.services.classroom_state import build_classroom_state
from app.services.phase3_views import mastery_view,roadmaps_view,progress_view,journal_view

@app.get('/users/{user_id}/classroom')
def classroom_state(user_id:str,course_id:str|None=None,db:Session=Depends(get_db)):
    if not db.get(User,user_id): raise HTTPException(404,'User not found')
    return build_classroom_state(db,user_id,course_id)

@app.get('/users/{user_id}/mastery-view')
def mastery_ui(user_id:str,db:Session=Depends(get_db)):
    if not db.get(User,user_id): raise HTTPException(404,'User not found')
    return mastery_view(db,user_id)
@app.get('/users/{user_id}/roadmaps-view')
def roadmaps_ui(user_id:str,db:Session=Depends(get_db)):
    if not db.get(User,user_id): raise HTTPException(404,'User not found')
    return roadmaps_view(db,user_id)
@app.get('/users/{user_id}/progress-view')
def progress_ui(user_id:str,db:Session=Depends(get_db)):
    if not db.get(User,user_id): raise HTTPException(404,'User not found')
    return progress_view(db,user_id)
@app.get('/users/{user_id}/journal-view')
def journal_ui(user_id:str,db:Session=Depends(get_db)):
    if not db.get(User,user_id): raise HTTPException(404,'User not found')
    return journal_view(db,user_id)

@app.post('/users/{user_id}/uploads')
async def upload_learning_file(user_id:str,file:UploadFile=File(...),assignment_id:str|None=Form(None),college_course_id:str|None=Form(None),title:str|None=Form(None),db:Session=Depends(get_db)):
    if not db.get(User,user_id): raise HTTPException(404,'User not found')
    if file.content_type not in ALLOWED: raise HTTPException(415,'Use JPG, PNG, WEBP, or PDF.')
    data=await file.read(MAX_BYTES+1)
    if len(data)>MAX_BYTES: raise HTTPException(413,'Maximum file size is 15 MB.')
    saved=storage.put(user_id=user_id,content_type=file.content_type,data=data)
    rec=FileRecord(user_id=user_id,filename=file.filename or 'upload',storage_key=saved['storage_key'],mime_type=file.content_type,size_bytes=saved['size_bytes']); db.add(rec); db.flush()
    if college_course_id:
        cc=db.query(CollegeCourse).filter_by(id=college_course_id,user_id=user_id).first()
        if not cc: raise HTTPException(404,'College course not found')
    if assignment_id:
        a=db.query(Assignment).filter_by(id=assignment_id,user_id=user_id).first()
        if not a: raise HTTPException(404,'Assignment not found')
    res=LearningResource(user_id=user_id,title=title or rec.filename,resource_type='file',file_id=rec.id,concept_ids=[],metadata_json={'assignment_id':assignment_id,'college_course_id':college_course_id,'purpose':'homework' if assignment_id else 'learning_material'}); db.add(res); db.commit(); db.refresh(res)
    return {'id':res.id,'file_id':rec.id,'title':res.title,'resource_type':'file','mastery_changed':False}

# --- Full Product Integration foundation: Phase 4-8 intelligence ---
from app.intelligence.integrated import teacher_turn as integrated_teacher_turn,next_learning_action,retention_interval,application_score,trading_process,personalization

@app.get('/integration/status')
def integration_status():
    return {'phase':'full_product_integration','base':'phase3_authoritative','systems':['teacher','mastery','retention','application','personalization'],'mock_ai':__import__('os').getenv('AI_PROVIDER','mock').lower()!='openai','ai_provider':__import__('os').getenv('AI_PROVIDER','mock'),'ai_model':__import__('os').getenv('OPENAI_MODEL','gpt-6-luna')}

@app.post('/users/{user_id}/teacher/turn')
def integrated_turn(user_id:str,mode:str,topic:str,help_level:int=0,db:Session=Depends(get_db)):
    if not db.get(User,user_id): raise HTTPException(404,'User not found')
    t=integrated_teacher_turn(mode,topic,help_level)
    return {'mode':t.mode,'message':t.message,'help_level':t.help_level,'action':t.action}

@app.get('/users/{user_id}/today/next')
def integrated_today(user_id:str,db:Session=Depends(get_db)):
    if not db.get(User,user_id): raise HTTPException(404,'User not found')
    repair=db.query(RepairSession).filter_by(user_id=user_id,status='open').first() is not None
    gate=db.query(DailyGate).filter_by(user_id=user_id,status='pending').first() is not None
    from datetime import datetime as _dt
    retention=db.query(ReviewSchedule).filter(ReviewSchedule.user_id==user_id,ReviewSchedule.next_due_at<=_dt.utcnow()).first() is not None
    enrollment=db.query(Enrollment).filter_by(user_id=user_id,active=True).first()
    return {'next_action':next_learning_action(repair=repair,daily_gate=gate,retention=retention,current_lesson=bool(enrollment and enrollment.current_lesson_id))}

@app.post('/users/{user_id}/application/trading-score')
def integrated_trade(user_id:str,plan:float,risk:float,execution:float,discipline:float,review:float,pnl:float,rule_breaks:int=0,db:Session=Depends(get_db)):
    if not db.get(User,user_id): raise HTTPException(404,'User not found')
    result=trading_process(plan,risk,execution,discipline,review,pnl,rule_breaks)
    attempt=ApplicationAttempt(user_id=user_id,attempt_type='trading_simulation',help_level=0,score=result['readiness_credit'],process_json=result,outcome_json={'pnl':pnl,'profitable':pnl>0})
    db.add(attempt); db.commit(); db.refresh(attempt)
    return {**result,'attempt_id':attempt.id}

@app.post('/users/{user_id}/personalization/preview')
def integrated_personalization(user_id:str,preferred:str='visual',db:Session=Depends(get_db)):
    if not db.get(User,user_id): raise HTTPException(404,'User not found')
    ev=db.query(EvidenceEvent).filter_by(user_id=user_id).order_by(EvidenceEvent.created_at.asc()).all()
    history=[{'score':x.score,'help_level':x.hint_level} for x in ev]
    result=personalization(history=history,preferred=preferred)
    snap=PersonalizationSnapshot(user_id=user_id,profile_json=result,reason_codes={'source':'evidence_history','preferred':preferred})
    db.add(snap); db.commit(); db.refresh(snap)
    return {**result,'snapshot_id':snap.id}


# --- Live provider-backed AI Teacher (Responses API with deterministic fallback) ---
from pydantic import BaseModel as _BaseModel
from app.services.ai_provider import generate_with_fallback,ASSESSMENT_MODES

class LiveTeacherRequest(_BaseModel):
    mode:str='teach'
    topic:str
    learner_input:str=''
    help_level:int=0
    context:str=''

@app.post('/users/{user_id}/teacher/live')
def live_teacher(user_id:str,data:LiveTeacherRequest,db:Session=Depends(get_db)):
    if not db.get(User,user_id): raise HTTPException(404,'User not found')
    help_level=0 if data.mode in ASSESSMENT_MODES else max(0,min(6,data.help_level))
    result=generate_with_fallback(mode=data.mode,topic=data.topic,learner_input=data.learner_input,help_level=help_level,context=data.context)
    return {'message':result.text,'provider':result.provider,'model':result.model,'fallback':result.fallback,'mode':data.mode,'help_level':help_level}


# --- Context-aware persistent Classroom AI loop ---
from app.services.teacher_context import build_teacher_context,compact_teacher_context
from app.intelligence.integrated import next_learning_action as _next_learning_action
from app.services.ai_provider import generate_with_fallback as _generate_teacher,ASSESSMENT_MODES as _ASSESSMENT_MODES

class ClassroomTurnRequest(_BaseModel):
    message:str=''
    mode:str='teach'
    help_level:int=0
    course_id:str|None=None
    concept_id:str|None=None

@app.post('/users/{user_id}/teacher/classroom-turn')
def classroom_teacher_turn(user_id:str,data:ClassroomTurnRequest,db:Session=Depends(get_db)):
    if not db.get(User,user_id): raise HTTPException(404,'User not found')
    ctx=build_teacher_context(db,user_id,data.course_id)
    topic='current lesson'
    resolved_concept_id=data.concept_id
    if not resolved_concept_id:
        from app.services.lesson_engine import active_concept
        resolved=active_concept(db,user_id,data.course_id)
        resolved_concept_id=resolved.id if resolved else None
    if resolved_concept_id:
        concept=db.get(Concept,resolved_concept_id)
        if not concept: raise HTTPException(404,'Concept not found')
        topic=concept.name
    elif ctx.get('position'): topic=ctx['position'].get('lesson') or topic
    effective_help=0 if data.mode in _ASSESSMENT_MODES else max(0,min(6,data.help_level))
    result=_generate_teacher(mode=data.mode,topic=topic,learner_input=data.message,help_level=effective_help,context=compact_teacher_context(ctx))
    course_id=ctx.get('course',{}).get('id') if ctx.get('course') else None
    lesson_id=ctx.get('position',{}).get('lesson_id') if ctx.get('position') else None
    interaction=TutorInteraction(user_id=user_id,course_id=course_id,lesson_id=lesson_id,concept_id=resolved_concept_id,mode=data.mode,help_level=effective_help,learner_input=data.message,tutor_output=result.text,provider=result.provider,model_name=result.model,fallback=result.fallback)
    db.add(interaction)
    if effective_help>0:
        db.add(HelpEvent(user_id=user_id,concept_id=data.concept_id,level=effective_help,context=f'classroom:{data.mode}'))
    db.commit();db.refresh(interaction)
    # Evaluation is separate from tutoring. Without an explicit target concept, fail closed.
    from app.services.ai_evaluator import evaluate_and_apply
    evidence_result=evaluate_and_apply(db,user_id,learner_input=data.message,concept_id=resolved_concept_id,mode=data.mode,help_level=effective_help,topic=topic,context=compact_teacher_context(ctx))
    repair=db.query(RepairSession).filter_by(user_id=user_id,status='open').first() is not None
    gate=db.query(DailyGate).filter_by(user_id=user_id,status='pending').first() is not None
    retention=db.query(ReviewSchedule).filter(ReviewSchedule.user_id==user_id,ReviewSchedule.next_due_at<=datetime.utcnow()).first() is not None
    enrollment=db.query(Enrollment).filter_by(user_id=user_id,active=True).first()
    next_action=_next_learning_action(repair=repair,daily_gate=gate,retention=retention,current_lesson=bool(enrollment and enrollment.current_lesson_id))
    return {'interaction_id':interaction.id,'message':result.text,'provider':result.provider,'model':result.model,'fallback':result.fallback,'mode':data.mode,'help_level':effective_help,'next_action':next_action,'evidence_result':evidence_result,'context_summary':{'course':ctx.get('course'),'position':ctx.get('position'),'reviews_due':len(ctx.get('reviews_due',[])),'misconceptions':len(ctx.get('misconceptions',[]))}}


# --- Deterministic AI Classroom evidence bridge ---
from app.services.evidence_pipeline import EvidenceProposal,apply_validated_proposal

@app.post('/users/{user_id}/teacher/evidence')
def teacher_evidence(user_id:str,data:EvidenceProposal,db:Session=Depends(get_db)):
    if not db.get(User,user_id):raise HTTPException(404,'User not found')
    result=apply_validated_proposal(db,user_id,data)
    # The deterministic state resolver decides what comes next after any accepted evidence.
    repair=db.query(RepairSession).filter_by(user_id=user_id,status='open').first() is not None
    gate=db.query(DailyGate).filter_by(user_id=user_id,status='pending').first() is not None
    retention=db.query(ReviewSchedule).filter(ReviewSchedule.user_id==user_id,ReviewSchedule.next_due_at<=datetime.utcnow()).first() is not None
    enrollment=db.query(Enrollment).filter_by(user_id=user_id,active=True).first()
    result['next_action']=_next_learning_action(repair=repair,daily_gate=gate,retention=retention,current_lesson=bool(enrollment and enrollment.current_lesson_id))
    return result


# --- Built-in curriculum + lesson position engine ---
from app.services.curriculum_seed import seed_builtin_curriculum
from app.services.lesson_engine import course_tree,start_course,active_concept,learning_position as get_learning_position,advance_position

@app.get('/curriculum')
def builtin_curriculum(db:Session=Depends(get_db)):
    seeded=seed_builtin_curriculum(db)
    return [course_tree(db,c.id) for c in seeded.values()]

@app.post('/users/{user_id}/courses/{course_id}/start')
def start_learning_course(user_id:str,course_id:str,db:Session=Depends(get_db)):
    if not db.get(User,user_id):raise HTTPException(404,'User not found')
    try:e=start_course(db,user_id,course_id)
    except ValueError as x:raise HTTPException(404,str(x))
    c=active_concept(db,user_id,course_id)
    return {'course_id':course_id,'lesson_id':e.current_lesson_id,'active_concept':None if not c else {'id':c.id,'name':c.name}}

@app.get('/users/{user_id}/courses/{course_id}/position')
def learning_position(user_id:str,course_id:str,db:Session=Depends(get_db)):
    e=db.query(Enrollment).filter_by(user_id=user_id,course_id=course_id,active=True).first()
    if not e:raise HTTPException(404,'Enrollment not found')
    return get_learning_position(db,user_id,course_id)


@app.post('/users/{user_id}/courses/{course_id}/advance')
def advance_learning_position(user_id:str,course_id:str,db:Session=Depends(get_db)):
    if not db.get(User,user_id):raise HTTPException(404,'User not found')
    return advance_position(db,user_id,course_id)


@app.post('/dev/bootstrap')
def dev_bootstrap(db:Session=Depends(get_db)):
    import os
    if is_production() or os.getenv('LEARNING_OS_DEV_BOOTSTRAP','0')!='1':
        raise HTTPException(404,'Not found')
    u=db.query(User).filter_by(display_name='Local Learner').first()
    if not u:
        u=User(display_name='Local Learner',timezone='America/New_York');db.add(u);db.flush();db.add(PrivacySetting(user_id=u.id));db.commit();db.refresh(u)
    return {'id':u.id,'display_name':u.display_name}
