"""Build the LangGraph support workflow."""

from __future__ import annotations

from pathlib import Path

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from agentic_ai_project.nodes import SupportNodes
from agentic_ai_project.rag import DEFAULT_KB_PATH
from agentic_ai_project.state import SupportState


def conditional_router(state: SupportState) -> str:
    return state["next_step"]


def build_support_graph(
    model: str = "gpt-4o-mini",
    temperature: float = 0,
    kb_path: Path = DEFAULT_KB_PATH,
):
    nodes = SupportNodes(model=model, temperature=temperature, kb_path=kb_path)
    builder = StateGraph(SupportState)

    builder.add_node("triage", nodes.triage_node)
    builder.add_node("general", nodes.general_node)
    builder.add_node("billing", nodes.billing_node)
    builder.add_node("tech", nodes.tech_node)
    builder.add_node("human_support", nodes.human_support_node)
    builder.add_node("sentiment_analyzer", nodes.sentiment_analyzer_node)

    builder.add_edge(START, "triage")
    builder.add_conditional_edges(
        "triage",
        conditional_router,
        {
            "billing": "billing",
            "general": "general",
            "tech": "tech",
        },
    )

    builder.add_edge("general", "sentiment_analyzer")
    builder.add_conditional_edges(
        "billing",
        conditional_router,
        {
            "sentiment_analyzer": "sentiment_analyzer",
            "triage": "triage",
        },
    )
    builder.add_edge("tech", "sentiment_analyzer")

    builder.add_conditional_edges(
        "sentiment_analyzer",
        conditional_router,
        {
            "human_support": "human_support",
            "done": END,
        },
    )
    builder.add_edge("human_support", END)

    return builder.compile(checkpointer=InMemorySaver())
