"""
Orchestrator: a LangGraph state machine, not a single mega-agent.

WHY A ROUTER + SPECIALISTS INSTEAD OF ONE AGENT WITH ALL TOOLS
(this is the #1 question to be ready for):
  - Smaller, scoped toolsets per agent reduce hallucinated/incorrect tool
    calls — an LLM given 15 tools calls the wrong one far more often than
    one given 3 relevant ones.
  - Blast radius: if the billing agent is compromised via prompt injection,
    it still can't touch refund or session tools because it was never given
    them. A single mega-agent has no such boundary.
  - Independent iteration: you can improve the refund agent's prompt without
    risking a regression in the technical agent.

WEEK 1 SCOPE: classify -> route -> specialist drafts a response. No memory,
no guardrails, no real escalation queue yet — those are Week 2. The
`confidence` and `requires_human_approval` fields already exist in the
state on purpose, so Week 2 slots in without a redesign.
"""

from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

from app.llm_client import get_llm_client
from app.agents.billing import run_billing_agent
from app.agents.technical import run_technical_agent
from app.agents.refund import run_refund_agent
from app.agents.general import run_general_agent


class TicketState(TypedDict, total=False):
    ticket_text: str
    category: str
    tool_context: str
    response: str
    confidence: float
    requires_human_approval: bool


llm = get_llm_client()


def classify_node(state: TicketState) -> TicketState:
    category = llm.classify(state["ticket_text"])
    return {**state, "category": category}


def route_decision(state: TicketState) -> str:
    """Conditional edge: sends state to the matching specialist node.
    An unrecognized category always falls back to 'general' rather than
    raising — routing failures should degrade gracefully, not crash."""
    return state.get("category", "general")


def billing_node(state: TicketState) -> TicketState:
    return {**state, **run_billing_agent(state["ticket_text"], llm)}


def technical_node(state: TicketState) -> TicketState:
    return {**state, **run_technical_agent(state["ticket_text"], llm)}


def refund_node(state: TicketState) -> TicketState:
    return {**state, **run_refund_agent(state["ticket_text"], llm)}


def general_node(state: TicketState) -> TicketState:
    return {**state, **run_general_agent(state["ticket_text"], llm)}


def build_graph():
    graph = StateGraph(TicketState)

    graph.add_node("classify", classify_node)
    graph.add_node("billing", billing_node)
    graph.add_node("technical", technical_node)
    graph.add_node("refund", refund_node)
    graph.add_node("general", general_node)

    graph.set_entry_point("classify")

    graph.add_conditional_edges(
        "classify",
        route_decision,
        {
            "billing": "billing",
            "technical": "technical",
            "refund": "refund",
            "general": "general",
        },
    )

    for node in ["billing", "technical", "refund", "general"]:
        graph.add_edge(node, END)

    return graph.compile()


def run_ticket(ticket_text: str) -> TicketState:
    app_graph = build_graph()
    return app_graph.invoke({"ticket_text": ticket_text})
