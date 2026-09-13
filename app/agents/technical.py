from app.tools.mock_tools import restart_login_session
from app.llm_client import LLMClient


def run_technical_agent(ticket_text: str, llm: LLMClient) -> dict:
    """Scoped toolset: session/login utilities only. No billing or refund
    tool access — a technical ticket has no legitimate reason to touch money."""
    tool_context = restart_login_session()
    response = llm.generate_response("technical", ticket_text, tool_context)
    return {
        "category": "technical",
        "tool_context": tool_context,
        "response": response,
        "confidence": 0.85,
    }
