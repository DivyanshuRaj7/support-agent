from app.llm_client import LLMClient


def run_general_agent(ticket_text: str, llm: LLMClient) -> dict:
    """Fallback for anything the router can't confidently classify.
    Deliberately low confidence + no tools — this agent's job is to say
    'I'm not sure, routing to a human' rather than guess with tools it
    doesn't understand the context for."""
    response = llm.generate_response("general", ticket_text, "no_tool_context")
    return {
        "category": "general",
        "tool_context": "none",
        "response": response,
        "confidence": 0.4,
        "requires_human_approval": True,
    }
