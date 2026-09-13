# Multi-Agent Customer Support System — Week 1

A router agent classifies incoming support tickets and dispatches them to
scoped specialist agents (billing, technical, refund), each with its own
limited toolset. Runs fully offline with `MockLLM` — no API key required to
demo or grade.

## Run it

```bash
pip install -r requirements.txt --break-system-packages
python -m tests.test_routing        # sanity check, no API key needed
uvicorn app.main:app --reload       # start the API
curl -X POST http://localhost:8000/ticket -H "Content-Type: application/json" \
     -d '{"ticket_text": "I was charged twice this month"}'
```

Set `OPENAI_API_KEY` in the environment to use the real LLM instead of the
mock classifier/responder — no code changes needed, `get_llm_client()`
switches automatically.

## Architecture decisions (and the questions they answer)

| Decision | Why | Likely interview question |
|---|---|---|
| Router + specialist agents, not one mega-agent | Scoped toolsets cut wrong-tool-call rate and limit blast radius if one agent is compromised | "Why not one agent with all tools?" |
| `LLMClient` abstraction with Mock/OpenAI implementations | Swappable provider, testable without burning API calls or needing secrets | "How would you test this without hitting a real LLM every time?" |
| Refund agent always sets `requires_human_approval=True` | Money-moving actions never auto-execute from an LLM decision alone | "What stops the agent from refunding people automatically?" |
| Low-confidence tickets fall back to `general`, not a guess | Graceful degradation — routing failures shouldn't produce a wrong specialist's confident wrong answer | "What happens when the classifier is unsure?" |
| Gateway (FastAPI) knows nothing about LangGraph internals | Framework is swappable later without breaking the API contract | "What if you switched frameworks — how much breaks?" |

## Known gaps — intentional, addressed in later weeks

- **No auth/rate limiting yet** (Week 2) — this week proves the agent logic; production needs a real gateway.
- **No memory/RAG over past tickets** (Week 2) — every ticket is stateless right now.
- **No prompt-injection defense on `ticket_text`** (Week 2) — raw text currently flows into the LLM prompt.
- **No eval suite scoring accuracy against a labeled set** (Week 3) — `test_routing.py` only proves wiring, not quality.
- **No observability/cost logging** (Week 3).
- **No deployment/CI** (Week 3).

If asked "why isn't X done yet," the honest answer is the architecture was
deliberately staged so each layer builds on a working foundation instead of
guardrails and memory being bolted onto agent logic that wasn't proven yet.
