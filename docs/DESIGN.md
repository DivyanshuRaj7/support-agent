# Design Doc — Multi-Agent Support Orchestration System

## 1. High-level architecture

```
Client → FastAPI Gateway (auth, validation, rate limit)
              ↓
        Orchestrator (LangGraph state machine)
              ↓ classify
      ┌───────┼───────┬─────────┐
   Billing  Technical  Refund  General   ← each: scoped tools only
      │         │         │       │
   [tools]   [tools]   [tools]  [none]
              ↓
     Guardrail layer (output schema validation, risk check)
              ↓
     requires_human_approval? → Approval queue (Week 2)
              ↓ no                    ↓ yes
        Return response         Human reviews → then executes
              ↓
     Audit log (every decision, every tool call, reasoning trace)
```

## 2. Why LangGraph over a single-agent loop
A single agent with all tools has no natural boundary — a compromised or
confused reasoning step can call any tool. A graph with named nodes gives
us: (a) explicit state at every step, inspectable and loggable, (b)
conditional routing instead of "the LLM decides everything," (c) each
specialist independently testable.

## 3. RAG design — which of the three flavors, and why

**We are building Agentic RAG, not basic RAG.** The router already performs
multi-step reasoning (classify → decide → possibly re-classify on low
confidence) before any retrieval happens — that reasoning loop, extended in
Week 2, becomes: retrieve ticket history → decide if it's enough → retrieve
account/order data if not → then respond. That's the defining trait of
Agentic RAG: multiple deliberate retrieval decisions inside a reasoning
loop, versus basic RAG's single embed-and-fetch.

**Graph RAG is a stretch goal, not core**, and here's the honest reasoning:
our data has real relationships (a ticket links to an account, an account
links to past orders, an order links to a refund policy) — that's exactly
what Graph RAG is for. If time allows, model these as a small graph
(NetworkX or Neo4j) so a question like "has this account had refund issues
before across multiple orders" can be answered by traversal, not just
similarity search. This is what separates a portfolio project from a
basic-PDF-chatbot project — call it out explicitly to interviewers even if
you only partially build it, and say clearly which parts are built vs.
designed-but-not-implemented.

**Multilingual RAG is explicitly out of scope** — it solves a real problem
(cross-language retrieval) that isn't the problem this project is
demonstrating. Adding it would dilute focus rather than add depth. State
this as a deliberate scope decision if asked, not an oversight.

### 3a. Retrieval sub-graph (the "agentic" part, in detail)

This sits between `classify` and the specialist nodes as its own small
graph, not a single function call:

```
retrieve_ticket_history (vector search: past tickets for this account_id)
        ↓
assess_sufficiency (is this enough context, or do we need relational data?)
        ↓
   ┌────┴────┐
  yes         no
   ↓           ↓
proceed    retrieve_relational_context (Graph RAG: account → orders → tickets)
   ↓           ↓
   └────┬──────┘
        ↓
synthesize_context → hand off to specialist agent
```

New `TicketState` fields (added in Week 2, additive — see 3b):
`retrieved_history: list[str]`, `retrieval_sufficient: bool`,
`graph_context: Optional[str]`.

**Key reliability decision — who decides "sufficient"?**
- *LLM-judged* (the agentic-textbook version): an LLM call reasons over the
  retrieved history and decides if it needs the graph too. Flexible, but
  adds latency + cost per ticket, and is harder to test deterministically.
- *Fixed rule* (e.g. "always check the graph for refund/billing tickets,
  never for technical"): cheap, deterministic, trivially testable.

**Decision: start with the fixed rule**, ship the LLM-judged version only as
a stretch. Reliability is one of the six production-AI skills this project
is meant to demonstrate — a fixed rule that works every time beats a
flashier agentic version that's flaky 5% of the time. Say this trade-off
out loud if asked "why isn't the agent deciding this itself."

### 3b. Why Week 1 needs no code changes for this
`TicketState` was declared with `total=False`, so it's additive by design —
the new fields above slot in without touching classify/route/specialist
logic from Week 1. This was intentional (see `orchestrator.py` comments on
`confidence`/`requires_human_approval`), and now covers the RAG fields too.

## 4. Guardrails (Week 2)
- **Input:** delimit user text clearly from system instructions in the
  prompt template; strip/flag suspicious control sequences; never let raw
  ticket text become a tool-call argument without validation
- **Output:** validate every agent response against a Pydantic schema
  before it leaves the graph; reject and retry once on schema failure
- **Action-level:** a fixed allow-list of which agent can call which tool
  (already true from Week 1 — this section documents it as policy, not
  accident)

## 5. Evals (Week 3)
- Build a ~30–50 item labeled ticket set (ticket_text → expected_category)
- Score: routing accuracy, false-escalation rate, false-auto-resolve rate
  (the second is worse than the first — flag this trade-off explicitly)
- Run the eval suite in CI on every prompt/graph change — this is what
  "we tested our AI system before shipping" actually looks like

## 6. Observability
- Structured logs per ticket: category, confidence, tools called, latency,
  token cost, human-approval outcome
- One dashboard question this must answer: "why did ticket #X get routed
  where it did, and what did it cost us?"

## 7. Pre-ship checklist (apply after every feature, not just at the end)
Before merging any new node/feature, answer:
1. Did I build this the most secure way? (inputs validated, tools scoped,
   no secrets logged)
2. Did I build this the most efficient way? (token cost, latency, does it
   scale past a demo)
3. What regressions could this introduce? (does it break an earlier
   working node?)
4. What tests do I need before shipping this? (unit test + eval-suite entry
   if it touches routing/response quality)

## 8. Design references (cited, not copied)
Papers/posts that directly shaped specific decisions above — cite these by
name if asked "why does this look the way it does":

- **ReAct** (reasoning + acting, Yao et al.) — the `assess_sufficiency` node
  in the retrieval sub-graph (3a) directly follows this pattern: reason
  about whether current context is enough → act by retrieving more if not
  → repeat, rather than retrieving once and hoping.
- **Anthropic, "Building Effective Agents"** — justifies the router +
  scoped-specialist architecture (section 2) over a single mega-agent;
  their framing of "workflows vs. agents" is why classify→route is a fixed
  workflow while the retrieval sub-graph is the one place we allow more
  autonomous looping.
- **OWASP Top 10 for LLM Applications** — the guardrails section (4) input/
  output validation rules map directly to their prompt-injection and
  insecure-output-handling categories; cite the category number, not just
  "we added guardrails," when explaining the design.
