"""
Runs the full graph for one ticket per category using MockLLM (no API key
needed). This is NOT the Week 3 eval suite (that scores accuracy against a
labeled set) — this just proves the pipeline wires together correctly.
"""

from app.orchestrator import run_ticket

TEST_TICKETS = [
    ("I was charged twice on my last invoice", "billing"),
    ("The app keeps crashing when I try to log in", "technical"),
    ("I want a refund for my order, it arrived broken", "refund"),
    ("What are your business hours?", "general"),
]


def test_routing():
    for ticket_text, expected_category in TEST_TICKETS:
        result = run_ticket(ticket_text)
        assert result["category"] == expected_category, (
            f"'{ticket_text}' routed to {result['category']}, expected {expected_category}"
        )
        assert result["response"], "response should not be empty"
        print(f"[OK] '{ticket_text[:40]}...' -> {result['category']} "
              f"(confidence={result['confidence']})")


if __name__ == "__main__":
    test_routing()
    print("\nAll routing tests passed.")
