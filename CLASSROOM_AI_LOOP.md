# Context-aware Classroom AI loop

The Classroom now has a complete server-side turn path:

1. Load the learner's active course and saved lesson.
2. Assemble lesson concepts, mastery, due reviews, unresolved misconceptions and recent tutor turns.
3. Add journal text only when the existing journal privacy setting explicitly permits AI access.
4. Force zero-help in assessment modes.
5. Send compact context + learner work to the configured Teacher provider.
6. Persist the learner input and tutor output in `tutor_interactions`.
7. Persist nonzero help usage.
8. Recompute the deterministic Learning OS next action and return it with the tutor response.

The AI does not directly mutate mastery in this endpoint. Evidence/mastery changes must go through deterministic evidence validation and the existing mastery service.

Frontend `LiveClassroom` is wired to this endpoint and shows an in-session conversation. Frontend production build remains pending because npm dependency retrieval is blocked in the current execution environment.
