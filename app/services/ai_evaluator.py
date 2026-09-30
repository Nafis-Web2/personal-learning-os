
from __future__ import annotations
import json,os
from dataclasses import dataclass
from pydantic import BaseModel,Field,ValidationError
from app.services.evidence_pipeline import EvidenceProposal,apply_validated_proposal

class EvaluationOutput(BaseModel):
    should_record:bool=False
    concept_id:str|None=None
    dimensions:dict[str,float]=Field(default_factory=dict)
    observable:bool=False
    correct:bool|None=None
    learner_confidence:str|None=None
    misconception:str|None=None
    rationale:str=''

def evaluator_instructions(mode:str,help_level:int)->str:
    return f"""You are an evidence evaluator, not the tutor.
Evaluate only the learner's observable work in the supplied turn.
Mode: {mode}. Recorded help level: {help_level}.
Never infer mastery from merely reading/watching material, asking a question, or receiving an explanation.
Do not reward the tutor's words. Score only what the learner independently demonstrated.
Use only: recall, understanding, application, transfer, independence, retention.
Return should_record=false if there is insufficient observable evidence or no unambiguous target concept.
A wrong answer can still be observable evidence and should include low scores plus a concise misconception when justified.
Do not change thresholds, unlock lessons, schedule reviews, or award mastery. The deterministic Learning OS does that."""

class Evaluator:
    def evaluate(self,*,learner_input:str,concept_id:str|None,mode:str,help_level:int,topic:str,context:str='')->EvaluationOutput:
        raise NotImplementedError

class MockEvaluator(Evaluator):
    def evaluate(self,**kwargs)->EvaluationOutput:
        # Offline mode deliberately cannot invent scores from natural language.
        return EvaluationOutput(should_record=False,rationale='Offline evaluator does not infer mastery scores.')

class OpenAIEvaluator(Evaluator):
    def __init__(self):
        from openai import OpenAI
        self.client=OpenAI(api_key=os.getenv('OPENAI_API_KEY'));self.model=os.getenv('OPENAI_EVALUATOR_MODEL',os.getenv('OPENAI_MODEL','gpt-6-luna'))
    def evaluate(self,*,learner_input,concept_id,mode,help_level,topic,context='')->EvaluationOutput:
        # JSON schema output is parsed locally as a second safety boundary.
        prompt=json.dumps({'target_concept_id':concept_id,'topic':topic,'learner_input':learner_input,'context':context},ensure_ascii=False)
        response=self.client.responses.create(model=self.model,instructions=evaluator_instructions(mode,help_level),input=prompt,
          text={'format':{'type':'json_schema','name':'learning_evidence','strict':True,'schema':EvaluationOutput.model_json_schema()}})
        return EvaluationOutput.model_validate_json(response.output_text)

def get_evaluator()->Evaluator:
    if os.getenv('AI_PROVIDER','mock').lower()=='openai' and os.getenv('OPENAI_API_KEY'):
        try:return OpenAIEvaluator()
        except Exception:return MockEvaluator()
    return MockEvaluator()

def evaluate_and_apply(db,user_id:str,*,learner_input:str,concept_id:str|None,mode:str,help_level:int,topic:str,context:str=''):
    if not learner_input.strip():return {'evaluated':False,'accepted':False,'reason':'no_learner_work','mastery_updated':False}
    try:out=get_evaluator().evaluate(learner_input=learner_input,concept_id=concept_id,mode=mode,help_level=help_level,topic=topic,context=context)
    except (ValidationError,ValueError,TypeError,json.JSONDecodeError):
        return {'evaluated':False,'accepted':False,'reason':'invalid_evaluator_output','mastery_updated':False}
    except Exception:
        return {'evaluated':False,'accepted':False,'reason':'evaluator_unavailable','mastery_updated':False}
    if not out.should_record:return {'evaluated':True,'accepted':False,'reason':'insufficient_observable_evidence','rationale':out.rationale,'mastery_updated':False}
    if not concept_id or out.concept_id!=concept_id:
        return {'evaluated':True,'accepted':False,'reason':'concept_identity_mismatch','mastery_updated':False}
    proposal=EvidenceProposal(concept_id=concept_id,dimensions=out.dimensions,observable=out.observable,correct=out.correct,
      learner_confidence=out.learner_confidence,misconception=out.misconception,rationale=out.rationale,mode=mode,help_level=help_level)
    return {'evaluated':True,**apply_validated_proposal(db,user_id,proposal)}
