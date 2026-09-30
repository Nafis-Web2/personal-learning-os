from pydantic import BaseModel,Field
class UserCreate(BaseModel):
    display_name:str=Field(min_length=1,max_length=120); timezone:str='America/New_York'
class JournalCreate(BaseModel):
    body:str=Field(min_length=1); entry_type:str='personal'; tags:list[str]=Field(default_factory=list)
class EvidenceCreate(BaseModel):
    concept_id:str; dimension:str; score:float=Field(ge=0,le=100); hint_level:int=Field(default=0,ge=0,le=6); source:str='lesson'; rationale:str|None=None
class ReviewCreate(BaseModel):
    concept_id:str; score:float=Field(ge=0,le=100)
class GateCreate(BaseModel): course_id:str; concept_ids:list[str]
class GateComplete(BaseModel): status:str; summary:str|None=None
class MisconceptionCreate(BaseModel): concept_id:str; description:str=Field(min_length=1); confidence:str|None=None
class PrivacyUpdate(BaseModel): journal_ai_access:str
class FileMetaCreate(BaseModel): filename:str; storage_key:str; mime_type:str|None=None; size_bytes:int=0; checksum:str|None=None; course_id:str|None=None
from datetime import datetime
class ExternalLearningCreate(BaseModel):
    source:str=Field(min_length=1,max_length=200); topic:str=Field(min_length=1,max_length=300); covered:str=''; source_url:str|None=None; minutes:int|None=Field(default=None,ge=0)
class CollegeCourseCreate(BaseModel):
    code:str=Field(min_length=1,max_length=80); title:str=Field(min_length=1,max_length=300); term:str|None=None
class HomeworkCreate(BaseModel):
    college_course_id:str|None=None; title:str=Field(min_length=1,max_length=300); notes:str=''; due_at:datetime|None=None
class ResourceCreate(BaseModel):
    title:str=Field(min_length=1,max_length=300); resource_type:str; url:str|None=None; file_id:str|None=None; concept_ids:list[str]=Field(default_factory=list); metadata_json:dict=Field(default_factory=dict)
class MediaUsageCreate(BaseModel):
    action:str='viewed'; seconds:int|None=Field(default=None,ge=0)
