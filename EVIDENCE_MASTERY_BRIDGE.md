# Evidence → Mastery bridge

The Classroom now has a deterministic state-changing path.

`POST /users/{user_id}/teacher/evidence`

A Teacher/evaluator may propose:
- concept ID
- observed dimensions and scores
- whether performance was observable
- correctness
- learner confidence
- misconception description
- mode and help level
- rationale

The validator—not the model—decides whether the proposal is eligible.

Rules:
- unknown concepts are rejected;
- non-observable activity is rejected;
- only six mastery dimensions are accepted;
- assessment modes are treated as help 0;
- help level 6 is ineligible until a fresh independent retest;
- heavy help caps evidence strength;
- wrong/high-confidence or weak responses can open targeted repair;
- accepted evidence updates EvidenceEvent, ConceptMastery and MasteryHistory;
- accepted performance updates the spaced ReviewSchedule;
- Daily Gate evidence updates its matching gate item and gate outcome;
- the deterministic next-action resolver runs after the state change.

The AI provider itself still has no direct permission to write mastery.
