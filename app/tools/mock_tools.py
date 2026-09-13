"""
Mock backend tools.

WHY MOCKED: in a real deployment these hit your billing DB, order system, etc.
Mocking them here lets you demo the FULL agent flow without needing real
infrastructure, while keeping the function signatures identical to what
production tools would look like — swap the body, not the interface.

WHY SEPARATE FUNCTIONS PER DOMAIN (interview talking point):
Each specialist agent is only given the tool functions relevant to it. The
billing agent never receives `check_refund_eligibility` even though it could
technically call it. Scoping tool access per agent is a security boundary:
it shrinks the blast radius if a prompt injection tries to get an agent to
call a tool it shouldn't.
"""

MOCK_ACCOUNTS = {
    "acc_123": {"balance_due": 49.99, "last_invoice": "INV-2026-08", "plan": "Pro"},
}

MOCK_ORDERS = {
    "ord_456": {"status": "delivered", "amount": 120.00, "days_since_purchase": 12},
}


def get_account_balance(account_id: str = "acc_123") -> str:
    acct = MOCK_ACCOUNTS.get(account_id, {})
    return f"balance_due=${acct.get('balance_due')}, plan={acct.get('plan')}"


def get_order_status(order_id: str = "ord_456") -> str:
    order = MOCK_ORDERS.get(order_id, {})
    return f"status={order.get('status')}, amount=${order.get('amount')}"


def check_refund_eligibility(order_id: str = "ord_456") -> str:
    order = MOCK_ORDERS.get(order_id, {})
    days = order.get("days_since_purchase", 999)
    eligible = days <= 30
    return f"eligible={eligible} (within 30-day window: {days} days since purchase)"


def restart_login_session(account_id: str = "acc_123") -> str:
    return "session_cleared=true, user should retry login"
