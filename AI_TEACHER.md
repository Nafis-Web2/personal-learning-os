# AI Teacher provider

The application now supports two server-side providers:

- `AI_PROVIDER=mock` — deterministic offline tutor, default.
- `AI_PROVIDER=openai` — OpenAI Responses API.

Current OpenAI SDK pattern used:
`OpenAI().responses.create(model=..., instructions=..., input=...)`
and reads `response.output_text`.

Recommended personal-development configuration:
```env
AI_PROVIDER=openai
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-6-luna
```

The key belongs only on the backend. Never use `NEXT_PUBLIC_OPENAI_API_KEY`.

Assessment modes force help level 0 before the provider is called. Full-explanation help requires a fresh independent retest before mastery credit. Provider failures fall back to the deterministic tutor so the Learning OS remains usable offline.

No live OpenAI request is executed by the test suite and no API key is included in this package.
