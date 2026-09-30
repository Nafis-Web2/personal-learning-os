
from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Protocol

ASSESSMENT_MODES={"assessment","daily_gate","cold_test","weekly_synthesis"}

@dataclass
class AIResult:
    text:str
    provider:str
    model:str
    fallback:bool=False

class TeacherProvider(Protocol):
    def generate(self, *, mode:str, topic:str, learner_input:str="", help_level:int=0, context:str="") -> AIResult: ...

def teacher_instructions(mode:str, help_level:int)->str:
    locked=mode in ASSESSMENT_MODES
    effective_help=0 if locked else max(0,min(6,int(help_level)))
    return f"""You are the AI Teacher inside a private Personal Learning OS.
Your job is to help the learner learn, prove, retain, and apply knowledge.
Mode: {mode}. Effective help level: {effective_help}.
Never claim mastery from conversation alone. Never invent evidence.
Require active learner work: retrieval, explanation, prediction, solving, debugging, or application.
Do not reveal hidden answers during independent assessments.
If mode is assessment, daily_gate, cold_test, or weekly_synthesis, provide zero hints and do not reveal the solution.
Help ladder: 0 independent; 1 Socratic question; 2 conceptual hint; 3 directional hint; 4 first step; 5 partial solution; 6 full explanation.
At help level 6, teach clearly but require a fresh independent retest before any mastery credit.
Prefer concise tutoring turns and usually end with one concrete learner action or question.
Adapt explanation style without lowering mastery standards or prerequisite gates."""

class MockTeacherProvider:
    def generate(self, *, mode:str, topic:str, learner_input:str="", help_level:int=0, context:str="")->AIResult:
        from app.intelligence.integrated import teacher_turn
        t=teacher_turn(mode,topic,help_level)
        return AIResult(text=t.message,provider="mock",model="deterministic",fallback=False)

class OpenAITeacherProvider:
    def __init__(self, api_key:str|None=None, model:str|None=None):
        from openai import OpenAI
        self.model=model or os.getenv("OPENAI_MODEL","gpt-6-luna")
        self.client=OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
    def generate(self, *, mode:str, topic:str, learner_input:str="", help_level:int=0, context:str="")->AIResult:
        prompt=f"Topic: {topic}\n"
        if context: prompt+=f"Relevant Learning OS context:\n{context}\n"
        prompt+=f"Learner message/work:\n{learner_input or '[No learner response yet]'}"
        response=self.client.responses.create(
            model=self.model,
            instructions=teacher_instructions(mode,help_level),
            input=prompt,
        )
        return AIResult(text=response.output_text.strip(),provider="openai",model=self.model)

def get_teacher_provider()->TeacherProvider:
    provider=os.getenv("AI_PROVIDER","mock").lower().strip()
    if provider=="openai" and os.getenv("OPENAI_API_KEY"):
        try:return OpenAITeacherProvider()
        except Exception:return MockTeacherProvider()
    return MockTeacherProvider()

def generate_with_fallback(*,mode:str,topic:str,learner_input:str="",help_level:int=0,context:str="")->AIResult:
    provider=get_teacher_provider()
    try:return provider.generate(mode=mode,topic=topic,learner_input=learner_input,help_level=help_level,context=context)
    except Exception:
        fallback=MockTeacherProvider().generate(mode=mode,topic=topic,learner_input=learner_input,help_level=help_level,context=context)
        fallback.fallback=True
        return fallback
