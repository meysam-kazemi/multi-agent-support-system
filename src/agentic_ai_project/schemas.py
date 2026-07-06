"""Pydantic schemas for the support workflow API."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: Literal["human", "ai", "user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Customer support message.")
    user_id: str = Field(default="test-user", min_length=1)
    thread_id: str | None = Field(default=None)


class ResumeRequest(BaseModel):
    thread_id: str = Field(..., min_length=1)
    approved: bool = Field(
        default=True,
        description="Approve the drafted agent response when true.",
    )
    replacement_message: str = Field(
        default="",
        description="Human replacement response when approved is false.",
    )


class WorkflowResponse(BaseModel):
    messages: list[Message]
    metadata: dict[str, Any]
    interrupted: bool = False
    interrupt: dict[str, Any] | None = None


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str
