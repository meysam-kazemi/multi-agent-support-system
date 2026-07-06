"""State and message helpers for the support workflow."""

from __future__ import annotations

import operator
from typing import Annotated, Any, List, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage


class SupportState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    user_id: str
    sentiment: str
    department: str
    current_node: str
    next_step: str


def make_initial_state(user_query: str, user_id: str = "test-user") -> SupportState:
    return {
        "messages": [HumanMessage(content=user_query)],
        "user_id": user_id,
        "sentiment": "neutral",
        "department": "",
        "current_node": "",
        "next_step": "",
    }


def message_content(message: Any) -> str:
    return str(getattr(message, "content", message))


def new_messages(previous: list[BaseMessage], current: list[BaseMessage]) -> list[BaseMessage]:
    """Return only messages added by an agent invocation."""
    if len(current) >= len(previous):
        return current[len(previous) :]
    return current
