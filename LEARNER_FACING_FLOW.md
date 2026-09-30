# Learner-facing flow

The built-in curriculum is now connected to the primary UI path:

Today / Roadmaps → Start or Continue → saved Enrollment → active Module/Lesson/Concept → Classroom → Teacher → evidence/mastery → Continue when ready.

Progression is deterministic:
- a conversation or button click cannot advance a lesson;
- active concepts require Overall >=70, Understanding >=70 and Application >=70;
- prerequisite edges also enforce Understanding/Application >=70;
- once every concept in a lesson satisfies the gate, the lesson is marked complete and `Enrollment.current_lesson_id` advances;
- the next visit resumes from that saved lesson;
- blocked progression returns an explicit reason rather than silently moving forward.

Frontend:
- Today loads the real Python/Trading curricula.
- Roadmaps expands real modules and lessons.
- Start/Continue calls the backend and opens Classroom.
- Classroom shows module, lesson and active concept.
- Continue asks the deterministic backend to advance; it cannot override mastery.

The Next.js production build remains unverified in this execution environment because npm dependencies cannot be retrieved reliably. Backend/API behavior is tested independently.
