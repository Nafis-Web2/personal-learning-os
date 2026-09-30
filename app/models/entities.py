import uuid
from datetime import datetime
from sqlalchemy import String,Integer,Float,Boolean,DateTime,ForeignKey,Text,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from app.db.base import Base

def uid(): return str(uuid.uuid4())
def now(): return datetime.utcnow()

class User(Base):
    __tablename__='users'; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); display_name:Mapped[str]=mapped_column(String(120)); timezone:Mapped[str]=mapped_column(String(64),default='America/New_York'); created_at:Mapped[datetime]=mapped_column(DateTime,default=now)
class AuthIdentity(Base):
    __tablename__='auth_identities'; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id:Mapped[str]=mapped_column(ForeignKey('users.id')); provider:Mapped[str]=mapped_column(String(40)); provider_subject:Mapped[str]=mapped_column(String(200)); __table_args__=(UniqueConstraint('provider','provider_subject'),)
class PrivacySetting(Base):
    __tablename__='privacy_settings'; user_id:Mapped[str]=mapped_column(ForeignKey('users.id'),primary_key=True); journal_ai_access:Mapped[str]=mapped_column(String(32),default='private'); updated_at:Mapped[datetime]=mapped_column(DateTime,default=now,onupdate=now)
class Course(Base):
    __tablename__='courses'; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); code:Mapped[str]=mapped_column(String(40),unique=True); title:Mapped[str]=mapped_column(String(160)); version:Mapped[int]=mapped_column(Integer,default=1)
class Module(Base):
    __tablename__='modules'; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); course_id:Mapped[str]=mapped_column(ForeignKey('courses.id')); code:Mapped[str]=mapped_column(String(40)); title:Mapped[str]=mapped_column(String(160)); position:Mapped[int]=mapped_column(Integer); __table_args__=(UniqueConstraint('course_id','code'),)
class Lesson(Base):
    __tablename__='lessons'; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); module_id:Mapped[str]=mapped_column(ForeignKey('modules.id')); title:Mapped[str]=mapped_column(String(180)); position:Mapped[int]=mapped_column(Integer)
class Concept(Base):
    __tablename__='concepts'; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); lesson_id:Mapped[str]=mapped_column(ForeignKey('lessons.id')); name:Mapped[str]=mapped_column(String(180)); position:Mapped[int]=mapped_column(Integer)
class ConceptPrerequisite(Base):
    __tablename__='concept_prerequisites'; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); concept_id:Mapped[str]=mapped_column(ForeignKey('concepts.id')); prerequisite_concept_id:Mapped[str]=mapped_column(ForeignKey('concepts.id')); required_understanding:Mapped[float]=mapped_column(Float,default=70); required_application:Mapped[float]=mapped_column(Float,default=70); __table_args__=(UniqueConstraint('concept_id','prerequisite_concept_id'),)
class Enrollment(Base):
    __tablename__='enrollments'; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id:Mapped[str]=mapped_column(ForeignKey('users.id')); course_id:Mapped[str]=mapped_column(ForeignKey('courses.id')); active:Mapped[bool]=mapped_column(Boolean,default=True); current_lesson_id:Mapped[str|None]=mapped_column(ForeignKey('lessons.id'),nullable=True); __table_args__=(UniqueConstraint('user_id','course_id'),)
class LessonProgress(Base):
    __tablename__='lesson_progress'; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id:Mapped[str]=mapped_column(ForeignKey('users.id')); lesson_id:Mapped[str]=mapped_column(ForeignKey('lessons.id')); status:Mapped[str]=mapped_column(String(24),default='not_started'); updated_at:Mapped[datetime]=mapped_column(DateTime,default=now,onupdate=now); __table_args__=(UniqueConstraint('user_id','lesson_id'),)
class ConceptMastery(Base):
    __tablename__='concept_mastery'; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id:Mapped[str]=mapped_column(ForeignKey('users.id')); concept_id:Mapped[str]=mapped_column(ForeignKey('concepts.id')); recall:Mapped[float]=mapped_column(Float,default=0); understanding:Mapped[float]=mapped_column(Float,default=0); application:Mapped[float]=mapped_column(Float,default=0); transfer:Mapped[float]=mapped_column(Float,default=0); independence:Mapped[float]=mapped_column(Float,default=0); retention:Mapped[float]=mapped_column(Float,default=0); overall:Mapped[float]=mapped_column(Float,default=0); updated_at:Mapped[datetime]=mapped_column(DateTime,default=now,onupdate=now); __table_args__=(UniqueConstraint('user_id','concept_id'),)
class MasteryHistory(Base):
    __tablename__='mastery_history'; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id:Mapped[str]=mapped_column(ForeignKey('users.id')); concept_id:Mapped[str]=mapped_column(ForeignKey('concepts.id')); overall:Mapped[float]=mapped_column(Float); dimension:Mapped[str]=mapped_column(String(32)); dimension_score:Mapped[float]=mapped_column(Float); created_at:Mapped[datetime]=mapped_column(DateTime,default=now)
class EvidenceEvent(Base):
    __tablename__='evidence_events'; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id:Mapped[str]=mapped_column(ForeignKey('users.id')); concept_id:Mapped[str]=mapped_column(ForeignKey('concepts.id')); dimension:Mapped[str]=mapped_column(String(32)); score:Mapped[float]=mapped_column(Float); hint_level:Mapped[int]=mapped_column(Integer,default=0); source:Mapped[str]=mapped_column(String(40)); rationale:Mapped[str|None]=mapped_column(Text,nullable=True); created_at:Mapped[datetime]=mapped_column(DateTime,default=now)
class Misconception(Base):
    __tablename__='misconceptions'; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id:Mapped[str]=mapped_column(ForeignKey('users.id')); concept_id:Mapped[str]=mapped_column(ForeignKey('concepts.id')); description:Mapped[str]=mapped_column(Text); confidence:Mapped[str|None]=mapped_column(String(20),nullable=True); resolved:Mapped[bool]=mapped_column(Boolean,default=False); first_seen_at:Mapped[datetime]=mapped_column(DateTime,default=now); resolved_at:Mapped[datetime|None]=mapped_column(DateTime,nullable=True)
class ReviewSchedule(Base):
    __tablename__='review_schedule'; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id:Mapped[str]=mapped_column(ForeignKey('users.id')); concept_id:Mapped[str]=mapped_column(ForeignKey('concepts.id')); next_due_at:Mapped[datetime]=mapped_column(DateTime); interval_days:Mapped[int]=mapped_column(Integer,default=1); stage:Mapped[int]=mapped_column(Integer,default=0); last_result:Mapped[str|None]=mapped_column(String(32),nullable=True); __table_args__=(UniqueConstraint('user_id','concept_id'),)
class ReviewEvent(Base):
    __tablename__='review_events'; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id:Mapped[str]=mapped_column(ForeignKey('users.id')); concept_id:Mapped[str]=mapped_column(ForeignKey('concepts.id')); result:Mapped[str]=mapped_column(String(20)); score:Mapped[float]=mapped_column(Float); created_at:Mapped[datetime]=mapped_column(DateTime,default=now)
class DailyGate(Base):
    __tablename__='daily_gates'; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id:Mapped[str]=mapped_column(ForeignKey('users.id')); course_id:Mapped[str]=mapped_column(ForeignKey('courses.id')); status:Mapped[str]=mapped_column(String(20),default='pending'); summary:Mapped[str|None]=mapped_column(Text,nullable=True); created_at:Mapped[datetime]=mapped_column(DateTime,default=now); completed_at:Mapped[datetime|None]=mapped_column(DateTime,nullable=True)
class DailyGateItem(Base):
    __tablename__='daily_gate_items'; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); gate_id:Mapped[str]=mapped_column(ForeignKey('daily_gates.id')); concept_id:Mapped[str]=mapped_column(ForeignKey('concepts.id')); score:Mapped[float|None]=mapped_column(Float,nullable=True); result:Mapped[str|None]=mapped_column(String(20),nullable=True)
class RepairSession(Base):
    __tablename__='repair_sessions'; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id:Mapped[str]=mapped_column(ForeignKey('users.id')); gate_id:Mapped[str|None]=mapped_column(ForeignKey('daily_gates.id'),nullable=True); concept_id:Mapped[str]=mapped_column(ForeignKey('concepts.id')); gap:Mapped[str]=mapped_column(Text); status:Mapped[str]=mapped_column(String(20),default='open'); created_at:Mapped[datetime]=mapped_column(DateTime,default=now)
class HelpEvent(Base):
    __tablename__='help_events'; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id:Mapped[str]=mapped_column(ForeignKey('users.id')); concept_id:Mapped[str|None]=mapped_column(ForeignKey('concepts.id'),nullable=True); level:Mapped[int]=mapped_column(Integer); context:Mapped[str|None]=mapped_column(Text,nullable=True); created_at:Mapped[datetime]=mapped_column(DateTime,default=now)
class StudySession(Base):
    __tablename__='study_sessions'; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id:Mapped[str]=mapped_column(ForeignKey('users.id')); course_id:Mapped[str|None]=mapped_column(ForeignKey('courses.id'),nullable=True); lesson_id:Mapped[str|None]=mapped_column(ForeignKey('lessons.id'),nullable=True); mode:Mapped[str]=mapped_column(String(32),default='classroom'); started_at:Mapped[datetime]=mapped_column(DateTime,default=now); ended_at:Mapped[datetime|None]=mapped_column(DateTime,nullable=True)
class SessionSummary(Base):
    __tablename__='session_summaries'; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id:Mapped[str]=mapped_column(ForeignKey('users.id')); course_id:Mapped[str|None]=mapped_column(ForeignKey('courses.id'),nullable=True); summary:Mapped[str]=mapped_column(Text); unresolved_gaps:Mapped[str|None]=mapped_column(Text,nullable=True); next_step:Mapped[str|None]=mapped_column(Text,nullable=True); created_at:Mapped[datetime]=mapped_column(DateTime,default=now)
class JournalEntry(Base):
    __tablename__='journal_entries'; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id:Mapped[str]=mapped_column(ForeignKey('users.id')); entry_type:Mapped[str]=mapped_column(String(32),default='personal'); body:Mapped[str]=mapped_column(Text); tags:Mapped[str]=mapped_column(String(500),default=''); created_at:Mapped[datetime]=mapped_column(DateTime,default=now)
class LearningLog(Base):
    __tablename__='learning_logs'; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id:Mapped[str]=mapped_column(ForeignKey('users.id')); course_id:Mapped[str|None]=mapped_column(ForeignKey('courses.id'),nullable=True); body:Mapped[str]=mapped_column(Text); created_at:Mapped[datetime]=mapped_column(DateTime,default=now)
class FileRecord(Base):
    __tablename__='files'; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id:Mapped[str]=mapped_column(ForeignKey('users.id')); filename:Mapped[str]=mapped_column(String(255)); storage_key:Mapped[str]=mapped_column(String(500)); mime_type:Mapped[str|None]=mapped_column(String(120),nullable=True); size_bytes:Mapped[int]=mapped_column(Integer,default=0); checksum:Mapped[str|None]=mapped_column(String(128),nullable=True); created_at:Mapped[datetime]=mapped_column(DateTime,default=now)
class FileCourseLink(Base):
    __tablename__='file_course_links'; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); file_id:Mapped[str]=mapped_column(ForeignKey('files.id')); course_id:Mapped[str]=mapped_column(ForeignKey('courses.id')); __table_args__=(UniqueConstraint('file_id','course_id'),)

# --- Phase 3 learning intake / multimodal persistence ---
from sqlalchemy import JSON
class ExternalLearningEvent(Base):
    __tablename__='external_learning_events'; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id:Mapped[str]=mapped_column(ForeignKey('users.id'),index=True); source:Mapped[str]=mapped_column(String(200)); topic:Mapped[str]=mapped_column(String(300)); covered:Mapped[str]=mapped_column(Text,default=''); source_url:Mapped[str|None]=mapped_column(String(1000),nullable=True); minutes:Mapped[int|None]=mapped_column(Integer,nullable=True); status:Mapped[str]=mapped_column(String(40),default='awaiting_proof'); created_at:Mapped[datetime]=mapped_column(DateTime,default=now)
class CollegeCourse(Base):
    __tablename__='college_courses'; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id:Mapped[str]=mapped_column(ForeignKey('users.id'),index=True); code:Mapped[str]=mapped_column(String(80)); title:Mapped[str]=mapped_column(String(300)); term:Mapped[str|None]=mapped_column(String(120),nullable=True); active:Mapped[bool]=mapped_column(Boolean,default=True); created_at:Mapped[datetime]=mapped_column(DateTime,default=now); __table_args__=(UniqueConstraint('user_id','code','term'),)
class Assignment(Base):
    __tablename__='assignments'; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id:Mapped[str]=mapped_column(ForeignKey('users.id'),index=True); college_course_id:Mapped[str|None]=mapped_column(ForeignKey('college_courses.id'),nullable=True,index=True); title:Mapped[str]=mapped_column(String(300)); notes:Mapped[str]=mapped_column(Text,default=''); due_at:Mapped[datetime|None]=mapped_column(DateTime,nullable=True); status:Mapped[str]=mapped_column(String(40),default='awaiting_analysis'); created_at:Mapped[datetime]=mapped_column(DateTime,default=now)
class AssignmentItem(Base):
    __tablename__='assignment_items'; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); assignment_id:Mapped[str]=mapped_column(ForeignKey('assignments.id'),index=True); position:Mapped[int]=mapped_column(Integer); prompt:Mapped[str]=mapped_column(Text); concept_ids:Mapped[list]=mapped_column(JSON,default=list); help_level:Mapped[int]=mapped_column(Integer,default=0); completed:Mapped[bool]=mapped_column(Boolean,default=False)
class LearningResource(Base):
    __tablename__='learning_resources'; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id:Mapped[str]=mapped_column(ForeignKey('users.id'),index=True); title:Mapped[str]=mapped_column(String(300)); resource_type:Mapped[str]=mapped_column(String(40)); url:Mapped[str|None]=mapped_column(String(1000),nullable=True); file_id:Mapped[str|None]=mapped_column(ForeignKey('files.id'),nullable=True); concept_ids:Mapped[list]=mapped_column(JSON,default=list); metadata_json:Mapped[dict]=mapped_column(JSON,default=dict); created_at:Mapped[datetime]=mapped_column(DateTime,default=now)
class MediaUsageEvent(Base):
    __tablename__='media_usage_events'; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id:Mapped[str]=mapped_column(ForeignKey('users.id'),index=True); resource_id:Mapped[str]=mapped_column(ForeignKey('learning_resources.id'),index=True); action:Mapped[str]=mapped_column(String(40),default='viewed'); seconds:Mapped[int|None]=mapped_column(Integer,nullable=True); created_at:Mapped[datetime]=mapped_column(DateTime,default=now)
class LearnerNote(Base):
    __tablename__='learner_notes'; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id:Mapped[str]=mapped_column(ForeignKey('users.id'),index=True); body:Mapped[str]=mapped_column(Text); course_id:Mapped[str|None]=mapped_column(String(36),nullable=True); lesson_id:Mapped[str|None]=mapped_column(String(36),nullable=True); concept_id:Mapped[str|None]=mapped_column(String(36),nullable=True); created_at:Mapped[datetime]=mapped_column(DateTime,default=now)

# --- Full Product Integration persistent audit/state ---
class PersonalizationSnapshot(Base):
    __tablename__='personalization_snapshots'; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id:Mapped[str]=mapped_column(ForeignKey('users.id'),index=True); concept_id:Mapped[str|None]=mapped_column(ForeignKey('concepts.id'),nullable=True,index=True); profile_json:Mapped[dict]=mapped_column(JSON,default=dict); reason_codes:Mapped[dict]=mapped_column(JSON,default=dict); created_at:Mapped[datetime]=mapped_column(DateTime,default=now)
class ApplicationAttempt(Base):
    __tablename__='application_attempts'; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id:Mapped[str]=mapped_column(ForeignKey('users.id'),index=True); concept_id:Mapped[str|None]=mapped_column(ForeignKey('concepts.id'),nullable=True,index=True); attempt_type:Mapped[str]=mapped_column(String(40)); help_level:Mapped[int]=mapped_column(Integer,default=0); score:Mapped[float|None]=mapped_column(Float,nullable=True); process_json:Mapped[dict]=mapped_column(JSON,default=dict); outcome_json:Mapped[dict]=mapped_column(JSON,default=dict); created_at:Mapped[datetime]=mapped_column(DateTime,default=now)


# --- Classroom AI conversation persistence ---
class TutorInteraction(Base):
    __tablename__='tutor_interactions'
    id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
    user_id:Mapped[str]=mapped_column(ForeignKey('users.id'),index=True)
    course_id:Mapped[str|None]=mapped_column(ForeignKey('courses.id'),nullable=True,index=True)
    lesson_id:Mapped[str|None]=mapped_column(ForeignKey('lessons.id'),nullable=True)
    concept_id:Mapped[str|None]=mapped_column(ForeignKey('concepts.id'),nullable=True)
    mode:Mapped[str]=mapped_column(String(32),default='teach')
    help_level:Mapped[int]=mapped_column(Integer,default=0)
    learner_input:Mapped[str]=mapped_column(Text,default='')
    tutor_output:Mapped[str]=mapped_column(Text)
    provider:Mapped[str]=mapped_column(String(40),default='mock')
    model_name:Mapped[str]=mapped_column(String(120),default='deterministic')
    fallback:Mapped[bool]=mapped_column(Boolean,default=False)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=now,index=True)
