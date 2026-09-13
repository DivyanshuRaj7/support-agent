# PRD — Multi-Agent Support Orchestration System

## 1. Problem
Support teams (and by extension: claims triage, IT helpdesk, order operations —
this is a domain-agnostic pattern) handle high volumes of repetitive,
multi-category requests that need different tools, context, and risk
tolerance per category. A single generic chatbot either over-permissions
itself (security risk) or under-serves complex requests (bad UX).

## 2. Who this is for
- **Primary (real):** support/ops teams who want faster first-response with
  a human still approving anything risky.
- **Primary (portfolio purpose):** this document itself is a work sample —
  it demonstrates you can scope, design, and reason about a production AI
  system, not just call an LLM API.

## 3. Goals
- Route incoming requests to the right specialized agent with high accuracy
- Never let an agent take an irreversible/high-risk action without a human
  approving it first
- Keep the system explainable — every decision has a traceable reason
- Keep it cheap and fast enough to run per-ticket in production

## 4. Non-goals (v1)
- Not building a training pipeline / fine-tuning a model
- Not supporting real-time voice or multi-modal input
- Not multi-tenant / multi-org from day one (single-tenant demo scope)

## 5. Scope by phase
| Phase | Deliverable |
|---|---|
| Week 1 (done) | Router + 3 scoped specialist agents, mock tools, FastAPI gateway |
| Week 2 | Short-term conversation memory, long-term memory via Agentic RAG over past tickets, input/output guardrails, human-approval queue |
| Week 3 | Eval harness (labeled ticket set, accuracy/hallucination scoring), observability (tracing, cost logging), Docker + CI, audit trail / compliance log |
| Stretch | Graph RAG layer linking accounts↔orders↔tickets for cross-entity questions; cost-based model routing (cheap model for classification, expensive only for final draft) |

## 6. Success metrics
- Routing accuracy ≥ 90% on a held-out labeled ticket set (Week 3 eval)
- 100% of "high-risk" actions (refunds, account changes) pass through the
  human-approval queue — zero exceptions, this is a hard constraint, not a target
- P95 response latency under a defined budget (set once real LLM calls are
  benchmarked — placeholder, not guessed)
- Every agent decision has an audit log entry with reasoning trace

## 7. Risks
- Prompt injection via ticket text → mitigated by input sanitization + scoped
  tool access (an agent can only do damage with tools it was given)
- Over-confident wrong routing → mitigated by confidence threshold + fallback
  to human/general agent
- Memory/RAG retrieving stale or wrong account context → mitigated by
  scoping retrieval per ticket_id/account_id, never global search
