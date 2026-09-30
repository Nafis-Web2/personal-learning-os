
from sqlalchemy.orm import Session
from app.models import Course,Module,Lesson,Concept,ConceptPrerequisite,ConceptMastery,Enrollment,LessonProgress

def course_tree(db:Session,course_id:str):
    course=db.get(Course,course_id)
    mods=db.query(Module).filter_by(course_id=course_id).order_by(Module.position).all()
    return {'id':course.id,'code':course.code,'title':course.title,'modules':[{'id':m.id,'code':m.code,'title':m.title,'position':m.position,'lessons':[
      {'id':l.id,'title':l.title,'position':l.position,'concepts':[{'id':c.id,'name':c.name,'position':c.position} for c in db.query(Concept).filter_by(lesson_id=l.id).order_by(Concept.position).all()]}
      for l in db.query(Lesson).filter_by(module_id=m.id).order_by(Lesson.position).all()]} for m in mods]}

def ordered_lessons(db,course_id):
    return (db.query(Lesson).join(Module,Lesson.module_id==Module.id).filter(Module.course_id==course_id)
            .order_by(Module.position,Lesson.position).all())

def first_lesson(db,course_id):
    lessons=ordered_lessons(db,course_id);return lessons[0] if lessons else None

def start_course(db:Session,user_id:str,course_id:str):
    if not db.get(Course,course_id):raise ValueError('Course not found')
    lesson=first_lesson(db,course_id)
    e=db.query(Enrollment).filter_by(user_id=user_id,course_id=course_id).first()
    if not e:e=Enrollment(user_id=user_id,course_id=course_id,active=True,current_lesson_id=lesson.id if lesson else None);db.add(e)
    else:e.active=True;e.current_lesson_id=e.current_lesson_id or (lesson.id if lesson else None)
    if e.current_lesson_id:
        lp=db.query(LessonProgress).filter_by(user_id=user_id,lesson_id=e.current_lesson_id).first()
        if not lp:db.add(LessonProgress(user_id=user_id,lesson_id=e.current_lesson_id,status='in_progress'))
    db.commit();db.refresh(e);return e

def mastery_for(db,user_id,concept_id):
    return db.query(ConceptMastery).filter_by(user_id=user_id,concept_id=concept_id).first()

def prerequisite_status(db,user_id,concept_id):
    edges=db.query(ConceptPrerequisite).filter_by(concept_id=concept_id).all();missing=[]
    for edge in edges:
        m=mastery_for(db,user_id,edge.prerequisite_concept_id)
        if not m or m.understanding<edge.required_understanding or m.application<edge.required_application:
            pre=db.get(Concept,edge.prerequisite_concept_id)
            missing.append({'concept_id':edge.prerequisite_concept_id,'name':getattr(pre,'name',None),
              'required_understanding':edge.required_understanding,'required_application':edge.required_application,
              'understanding':0 if not m else m.understanding,'application':0 if not m else m.application})
    return {'unlocked':not missing,'missing':missing}

def concept_proficient(m):
    return bool(m and m.overall>=70 and m.understanding>=70 and m.application>=70)

def active_concept(db:Session,user_id:str,course_id:str|None=None):
    q=db.query(Enrollment).filter_by(user_id=user_id,active=True)
    e=q.filter_by(course_id=course_id).first() if course_id else q.first()
    if not e or not e.current_lesson_id:return None
    concepts=db.query(Concept).filter_by(lesson_id=e.current_lesson_id).order_by(Concept.position).all()
    for c in concepts:
        if not concept_proficient(mastery_for(db,user_id,c.id)):
            return c
    return None

def advance_position(db:Session,user_id:str,course_id:str):
    e=db.query(Enrollment).filter_by(user_id=user_id,course_id=course_id,active=True).first()
    if not e:return {'advanced':False,'reason':'not_enrolled'}
    current=active_concept(db,user_id,course_id)
    if current:
        status=prerequisite_status(db,user_id,current.id)
        m=mastery_for(db,user_id,current.id)
        if not status['unlocked']:
            return {'advanced':False,'reason':'prerequisite_blocked','concept':{'id':current.id,'name':current.name},'missing':status['missing']}
        if not concept_proficient(m):
            return {'advanced':False,'reason':'mastery_not_ready','concept':{'id':current.id,'name':current.name},
              'requirements':{'overall':70,'understanding':70,'application':70},
              'current':{'overall':0 if not m else m.overall,'understanding':0 if not m else m.understanding,'application':0 if not m else m.application}}
        return {'advanced':False,'reason':'continue_current_lesson'}
    # all concepts in current lesson are proficient: mark complete and move to next lesson
    lp=db.query(LessonProgress).filter_by(user_id=user_id,lesson_id=e.current_lesson_id).first()
    if lp:lp.status='completed'
    lessons=ordered_lessons(db,course_id);ids=[x.id for x in lessons]
    try:i=ids.index(e.current_lesson_id)
    except ValueError:return {'advanced':False,'reason':'lesson_not_in_course'}
    if i+1>=len(lessons):
        db.commit();return {'advanced':False,'reason':'course_complete','course_complete':True}
    nxt=lessons[i+1];e.current_lesson_id=nxt.id
    np=db.query(LessonProgress).filter_by(user_id=user_id,lesson_id=nxt.id).first()
    if not np:db.add(LessonProgress(user_id=user_id,lesson_id=nxt.id,status='in_progress'))
    db.commit();c=active_concept(db,user_id,course_id)
    return {'advanced':True,'lesson':{'id':nxt.id,'title':nxt.title},'active_concept':None if not c else {'id':c.id,'name':c.name}}

def learning_position(db:Session,user_id:str,course_id:str):
    e=db.query(Enrollment).filter_by(user_id=user_id,course_id=course_id,active=True).first()
    if not e:return None
    lesson=db.get(Lesson,e.current_lesson_id) if e.current_lesson_id else None
    module=db.get(Module,lesson.module_id) if lesson else None
    c=active_concept(db,user_id,course_id)
    lock=None if not c else prerequisite_status(db,user_id,c.id)
    m=None if not c else mastery_for(db,user_id,c.id)
    return {'course_id':course_id,'lesson':None if not lesson else {'id':lesson.id,'title':lesson.title},
      'module':None if not module else {'id':module.id,'code':module.code,'title':module.title},
      'active_concept':None if not c else {'id':c.id,'name':c.name},
      'concept_unlocked':True if not c else lock['unlocked'],'missing_prerequisites':[] if not lock else lock['missing'],
      'mastery':None if not m else {'overall':m.overall,'understanding':m.understanding,'application':m.application}}
