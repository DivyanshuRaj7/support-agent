from app.tools.mock_tools import get_account_balance
from app.llm_client import LLMClient


def run_billing_agent(ticket_text: str, llm: LLMClient) -> dict:
    """Scoped toolset: only account balance lookup. This agent CANNOT
    issue refunds or touch order data — that's the refund agent's job.
    Keeping scopes narrow is a deliberate security/blast-radius decision,
    not an oversight."""
    tool_context = get_account_balance()
    response = llm.generate_response("billing", ticket_text, tool_context)
    return {
        "category": "billing",
        "tool_context": tool_context,
        "response": response,
        "confidence": 0.9,
    }
