# Built-in curriculum engine

Learning OS now ships with two database-backed curricula.

## Python Foundations
14 modules (P0–P13): setup, values/variables, operators/conversion, strings, control flow, loops, collections, functions, debugging, files/modules, OOP, intermediate Python, testing/quality, foundation projects.

## Trading Foundations
13 modules (T0–T12): markets/instruments, styles, long/short/orders, volume/volatility/liquidity, catalysts/premarket, charts, VWAP/indicators, risk, setups/plans, execution/discipline, journaling, simulation, readiness.

Each course is seeded idempotently into Course → Module → Lesson → Concept records. Ordered concepts have 70 Understanding / 70 Application prerequisite edges.

`POST /users/{user}/courses/{course}/start` creates/resumes an Enrollment and persists `current_lesson_id`.
The lesson engine resolves an explicit active concept. Classroom turns now automatically attach that concept ID when the frontend does not supply one, so the evaluator no longer needs to guess a concept during normal built-in lessons.

The seed is intentionally curriculum structure, not a claim that static text alone is the lesson. The AI Teacher uses these targets to generate interactive teaching, retrieval and application.
