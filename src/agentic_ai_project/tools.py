"""Mock tools used by the support agents."""

from __future__ import annotations

from langchain_core.tools import tool


MOCK_SUBSCRIPTIONS = {
    "u1": "active",
    "u2": "expired",
    "u3": "canceled",
}

REFUNDABLE_TRANSACTIONS = {
    "tx-100": True,
    "tx-123": False,
    "tx-200": True,
}


@tool
def check_subscription_status(user_id: str) -> str:
    """Check subscription status for a user."""
    return MOCK_SUBSCRIPTIONS.get(user_id, "not_found")


@tool
def process_refund(transaction_id: str) -> bool:
    """Attempt to process a mock refund for a transaction."""
    return REFUNDABLE_TRANSACTIONS.get(transaction_id, False)
