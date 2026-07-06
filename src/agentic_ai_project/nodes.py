"""LangGraph node factory for the support workflow."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.types import interrupt
from pydantic import BaseModel

from agentic_ai_project.prompts import (
    BILLING_SYSTEM_PROMPT,
    GENERAL_SYSTEM_PROMPT,
    SENTIMENT_ANALYZER_SYSTEM_PROMPT,
    TECH_SYSTEM_PROMPT,
    TRIAGE_SYSTEM_PROMPT,
)
from agentic_ai_project.rag import DEFAULT_KB_PATH, build_vector_store
from agentic_ai_project.state import SupportState, new_messages
from agentic_ai_project.tools import check_subscription_status, process_refund


class TriageResponse(BaseModel):
    department: Literal["billing", "tech", "general"]


class SentimentResponse(BaseModel):
    sentiment: Literal["neutral", "positive", "negative"]


class SupportNodes:
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        temperature: float = 0,
        kb_path: Path = DEFAULT_KB_PATH,
    ) -> None:
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.triage_llm = self.llm.with_structured_output(TriageResponse)
        self.sentiment_llm = self.llm.with_structured_output(SentimentResponse)

        self.general_agent = create_agent(
            model=self.llm,
            tools=[],
            system_prompt=GENERAL_SYSTEM_PROMPT,
        )
        self.billing_agent = create_agent(
            model=self.llm,
            tools=[check_subscription_status, process_refund],
            system_prompt=BILLING_SYSTEM_PROMPT,
        )

        vector_store = build_vector_store(kb_path)

        @tool(response_format="content_and_artifact")
        def retrieve_context(query: str):
            """Retrieve information to help answer a technical support query."""
            retrieved = vector_store.similarity_search(query, k=2)
            serialized = "\n\n".join(
                f"Content{i + 1}: {chunk.page_content}" for i, chunk in enumerate(retrieved)
            )
            return serialized, retrieved

        self.tech_agent = create_agent(
            model=self.llm,
            tools=[retrieve_context],
            system_prompt=TECH_SYSTEM_PROMPT,
        )

    def triage_node(self, state: SupportState):
        prompt = TRIAGE_SYSTEM_PROMPT
        if state["current_node"] == "billing":
            prompt += "\n\nThis query is not relevant to Billing, so it is general or tech."

        response = self.triage_llm.invoke([SystemMessage(prompt)] + state["messages"])
        return {
            "department": response.department,
            "current_node": "triage",
            "next_step": response.department,
        }

    def general_node(self, state: SupportState):
        response = self.general_agent.invoke({"messages": state["messages"]})
        return {
            "messages": new_messages(state["messages"], response["messages"]),
            "department": "general",
            "current_node": "general",
            "next_step": "sentiment_analyzer",
        }

    def billing_node(self, state: SupportState):
        response = self.billing_agent.invoke({"messages": state["messages"]})
        added_messages = new_messages(state["messages"], response["messages"])
        answer = added_messages[-1].content if added_messages else ""

        if "not_relevant" in answer:
            return {
                "department": "billing",
                "current_node": "billing",
                "next_step": "triage",
            }

        return {
            "messages": added_messages,
            "department": "billing",
            "current_node": "billing",
            "next_step": "sentiment_analyzer",
        }

    def tech_node(self, state: SupportState):
        response = self.tech_agent.invoke({"messages": state["messages"]})
        return {
            "messages": new_messages(state["messages"], response["messages"]),
            "department": "tech",
            "current_node": "tech",
            "next_step": "sentiment_analyzer",
        }

    def sentiment_analyzer_node(self, state: SupportState):
        messages = [SystemMessage(SENTIMENT_ANALYZER_SYSTEM_PROMPT)] + state["messages"]
        response = self.sentiment_llm.invoke(messages)
        next_step = "human_support" if response.sentiment == "negative" else "done"
        return {
            "sentiment": response.sentiment,
            "current_node": "sentiment_analyzer",
            "next_step": next_step,
        }

    def human_support_node(self, state: SupportState):
        decision = interrupt(
            {
                "reason": "Negative sentiment detected",
                "query": state["messages"][-1],
                "sentiment": state["sentiment"],
                "question": "Should the drafted response be sent, or should a human replace it?",
            }
        )

        if decision["approved"]:
            return {"current_node": "human_support", "next_step": "done"}

        return {
            "messages": [AIMessage(content=decision["message"])],
            "current_node": "human_support",
            "next_step": "done",
        }
