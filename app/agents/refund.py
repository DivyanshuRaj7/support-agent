from app.tools.mock_tools import check_refund_eligibility
from app.llm_client import LLMClient


def run_refund_agent(ticket_text: str, llm: LLMClient) -> dict:
    """Highest-risk agent: refunds move money. In Week 1 this only drafts a
    recommendation — it does NOT execute anything. Week 2 adds a real
    human-approval gate before any refund action is taken. Flagging that
    distinction now (draft vs. execute) is a common interview question:
    'what stops the agent from just refunding people automatically?'"""
    tool_context = check_refund_eligibility()
    response = llm.generate_response("refund", ticket_text, tool_context)
    return {
        "category": "refund",
        "tool_context": tool_context,
        "response": response,
        "confidence": 0.8,
        "requires_human_approval": True,  # always true for this agent, non-negotiable
    }
