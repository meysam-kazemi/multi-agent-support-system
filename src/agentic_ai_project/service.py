"""Service wrapper around the support workflow graph."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from uuid import uuid4

from dotenv import load_dotenv
from langgraph.types import Command

from agentic_ai_project.graph import build_support_graph
from agentic_ai_project.rag import DEFAULT_KB_PATH
from agentic_ai_project.state import make_initial_state, message_content


@dataclass
class WorkflowResult:
    messages: list[dict[str, str]]
    metadata: dict[str, Any]
    interrupted: bool = False
    interrupt: dict[str, Any] | None = None

    @property
    def last_message(self) -> str:
        return self.messages[-1]["content"] if self.messages else ""


@dataclass
class SupportWorkflowService:
    model: str = "gpt-4o-mini"
    temperature: float = 0
    kb_path: Path = DEFAULT_KB_PATH
    graph: Any = field(init=False)

    def __post_init__(self) -> None:
        load_dotenv()
        self.graph = build_support_graph(
            model=self.model,
            temperature=self.temperature,
            kb_path=self.kb_path,
        )

    def new_thread_id(self, user_id: str = "test-user") -> str:
        return f"{user_id}-{uuid4().hex[:8]}"

    def run(self, user_query: str, user_id: str, thread_id: str | None = None) -> WorkflowResult:
        user_query = user_query.strip()
        user_id = (user_id or "test-user").strip()
        if not user_query:
            raise ValueError("user_query cannot be empty.")

        thread_id = thread_id or self.new_thread_id(user_id)
        config = {"configurable": {"thread_id": thread_id}}
        final_step = None

        for step in self.graph.stream(
            make_initial_state(user_query, user_id),
            config,
            stream_mode="values",
        ):
            final_step = step

        return self._to_result(final_step or {}, thread_id)

    def resume_human_review(
        self,
        thread_id: str,
        approved: bool,
        replacement_message: str = "",
    ) -> WorkflowResult:
        payload = {"approved": approved, "message": replacement_message.strip()}
        config = {"configurable": {"thread_id": thread_id}}
        final_step = None

        for step in self.graph.stream(Command(resume=payload), config, stream_mode="values"):
            final_step = step

        return self._to_result(final_step or {}, thread_id)

    def _to_result(self, step: dict[str, Any], thread_id: str) -> WorkflowResult:
        messages = [
            {"role": message.type, "content": message_content(message)}
            for message in step.get("messages", [])
            if getattr(message, "type", None) in {"human", "ai"}
        ]
        metadata = {
            "thread_id": thread_id,
            "department": step.get("department", ""),
            "sentiment": step.get("sentiment", ""),
            "current_node": step.get("current_node", ""),
            "next_step": step.get("next_step", ""),
        }

        interrupt_items = step.get("__interrupt__", [])
        if interrupt_items:
            interrupt_value = interrupt_items[0].value
            interrupt_payload = {
                "reason": interrupt_value.get("reason", ""),
                "sentiment": interrupt_value.get("sentiment", ""),
                "question": interrupt_value.get("question", ""),
                "query": message_content(interrupt_value.get("query", "")),
            }
            return WorkflowResult(
                messages=messages,
                metadata=metadata,
                interrupted=True,
                interrupt=interrupt_payload,
            )

        return WorkflowResult(messages=messages, metadata=metadata)
