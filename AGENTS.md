# AGENTS.md

Context for any coding agent (Muse Spark, Claude Code, etc.) working in this repo.

## Project
Multi-Agent Support Orchestration System — a portfolio project for AI/agentic
engineering internships. Domain-agnostic router + scoped-specialist pattern
(support tickets today; same shape fits claims triage, IT helpdesk, etc.).

## Read first
- `docs/PRD.md` — problem, goals, phased scope
- `docs/DESIGN.md` — architecture, RAG design, guardrails, references
- `docs/TECH_STACK.md` — tool choices and why each was picked over an alternative

## Working rules
1. Build ONE node/feature at a time. Never bundle several in one change.
2. After each feature, run this checklist before it's considered done:
   - Most secure way to build it?
   - Most efficient way?
   - What regressions could it introduce?
   - What tests does it need before shipping?
3. Everything must stay runnable with zero API keys (`MockLLM` fallback in
   `app/llm_client.py`). Never make a feature depend on a live key to even
   run/test.
4. `TicketState` (in `app/orchestrator.py`) is declared `total=False` on
   purpose — additive by design. New fields (memory, RAG) should extend it,
   never require refactoring existing nodes.
5. Tool access per agent is a fixed allow-list (see `app/tools/mock_tools.py`
   comments) — never give an agent a tool outside its domain, even if it
   would "just work."

## Run / test
```bash
pip install -r requirements.txt --break-system-packages
python -m tests.test_routing        # sanity check, no API key needed
uvicorn app.main:app --reload
```

## Current stage
Week 1 complete (routing + scoped agents, docs). Week 2 in progress:
memory, Agentic RAG retrieval sub-graph (see DESIGN.md §3a), guardrails,
human-approval queue.
