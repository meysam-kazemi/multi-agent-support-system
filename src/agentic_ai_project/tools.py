"""Mock tools used by the support agents."""

from __future__ import annotations

import random

from langchain_core.tools import tool


@tool
def check_subscription_status(user_id: str) -> str:
    """Check subscription status for a user."""
    mock_db = {
        "u1": "active",
        "u2": "expired",
        "u3": "canceled",
    }
    return mock_db.get(user_id, "not_found")


@tool
def process_refund(transaction_id: str) -> bool:
    """Attempt to process a mock refund for a transaction."""
    return random.random() < 0.5
