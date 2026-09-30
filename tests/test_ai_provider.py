
import os
from app.services.ai_provider import teacher_instructions,MockTeacherProvider,ASSESSMENT_MODES

def test_assessment_instructions_lock_help():
    x=teacher_instructions("assessment",5)
    assert "Effective help level: 0" in x
    assert "do not reveal the solution" in x

def test_mock_provider_is_offline():
    r=MockTeacherProvider().generate(mode="teach",topic="loops",help_level=2)
    assert r.provider=="mock" and r.model=="deterministic"

def test_help_six_requires_retest_instruction():
    assert "fresh independent retest" in teacher_instructions("teach",6)
