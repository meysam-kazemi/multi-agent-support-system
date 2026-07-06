"""Workflow orchestration around the compiled LangGraph graph."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langgraph.types import Command

from agentic_ai_project.graph import build_support_graph
from agentic_ai_project.rag import DEFAULT_KB_PATH
from agentic_ai_project.state import make_initial_state


@dataclass
class SupportWorkflowOrchestrator:
    """Owns graph construction and thread-scoped workflow execution."""

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

    def run_message(self, user_query: str, user_id: str, thread_id: str) -> dict[str, Any]:
        final_step: dict[str, Any] | None = None
        config = {"configurable": {"thread_id": thread_id}}

        for step in self.graph.stream(
            make_initial_state(user_query, user_id),
            config,
            stream_mode="values",
        ):
            final_step = step

        return final_step or {}

    def resume_human_review(
        self,
        thread_id: str,
        approved: bool,
        replacement_message: str = "",
    ) -> dict[str, Any]:
        final_step: dict[str, Any] | None = None
        config = {"configurable": {"thread_id": thread_id}}
        payload = {"approved": approved, "message": replacement_message}

        for step in self.graph.stream(Command(resume=payload), config, stream_mode="values"):
            final_step = step

        return final_step or {}
