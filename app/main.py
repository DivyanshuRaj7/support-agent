"""
Gateway layer.

WHY A SEPARATE GATEWAY (interview talking point):
The API layer knows nothing about LangGraph internals — it validates input,
calls the orchestrator, and shapes output. This separation means you could
swap the entire agent framework later without touching the API contract that
frontend/other services depend on.

Week 1: no auth yet (that's flagged below as a TODO for Week 2, alongside
rate limiting) — the point this week is proving the routing + agent logic
works end-to-end.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.orchestrator import run_ticket

app = FastAPI(title="Multi-Agent Support System", version="0.1.0")


class TicketRequest(BaseModel):
    ticket_text: str = Field(..., min_length=1, max_length=4000)


class TicketResponse(BaseModel):
    category: str
    response: str
    confidence: float
    requires_human_approval: bool = False


@app.post("/ticket", response_model=TicketResponse)
def submit_ticket(req: TicketRequest):
    if not req.ticket_text.strip():
        raise HTTPException(status_code=400, detail="ticket_text cannot be empty")

    result = run_ticket(req.ticket_text)

    return TicketResponse(
        category=result.get("category", "general"),
        response=result.get("response", ""),
        confidence=result.get("confidence", 0.0),
        requires_human_approval=result.get("requires_human_approval", False),
    )


@app.get("/health")
def health():
    return {"status": "ok"}
