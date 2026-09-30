# Closed learning loop

A Classroom turn now has two independent AI responsibilities:

1. **Teacher** — produces the learner-facing tutoring response.
2. **Evaluator** — produces only a structured evidence proposal.

The evaluator uses OpenAI Responses API Structured Outputs (`text.format` with strict JSON Schema) when the live provider is enabled. OpenAI's current documentation recommends Structured Outputs over basic JSON mode when schema adherence is required.

The evaluator cannot write mastery. Its output is parsed into `EvaluationOutput`, checked for an exact target concept match, converted into `EvidenceProposal`, and then passed through the deterministic evidence validator.

Fail-closed behavior:
- no explicit concept target → no automatic mastery;
- no learner work → no automatic mastery;
- malformed/unavailable evaluator → no automatic mastery;
- concept mismatch → no automatic mastery;
- offline mock evaluator → teaches normally but does not invent scores;
- non-observable work/help-level restrictions remain enforced downstream.

The Classroom response includes `evidence_result`, and the frontend shows accepted mastery/review/repair changes or explains that no mastery change occurred.
