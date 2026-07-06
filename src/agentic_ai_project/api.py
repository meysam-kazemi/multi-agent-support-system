"""FastAPI application for the agentic support workflow."""

from __future__ import annotations

from functools import lru_cache

from fastapi import FastAPI, HTTPException

from agentic_ai_project.schemas import (
    ChatRequest,
    HealthResponse,
    Message,
    ResumeRequest,
    WorkflowResponse,
)
from agentic_ai_project.service import SupportWorkflowService, WorkflowResult


@lru_cache(maxsize=1)
def get_service() -> SupportWorkflowService:
    return SupportWorkflowService()


def to_response(result: WorkflowResult) -> WorkflowResponse:
    return WorkflowResponse(
        messages=[Message(**message) for message in result.messages],
        metadata=result.metadata,
        interrupted=result.interrupted,
        interrupt=result.interrupt,
    )


app = FastAPI(
    title="Agentic AI Support Workflow",
    description="LangGraph-powered customer support orchestration API.",
    version="0.1.0",
)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="agentic-ai-project")


@app.post("/chat", response_model=WorkflowResponse, tags=["workflow"])
def chat(request: ChatRequest) -> WorkflowResponse:
    try:
        result = get_service().run(
            user_query=request.message,
            user_id=request.user_id,
            thread_id=request.thread_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return to_response(result)


@app.post("/human-review/resume", response_model=WorkflowResponse, tags=["workflow"])
def resume_human_review(request: ResumeRequest) -> WorkflowResponse:
    if not request.approved and not request.replacement_message.strip():
        raise HTTPException(
            status_code=400,
            detail="replacement_message is required when approved is false.",
        )

    result = get_service().resume_human_review(
        thread_id=request.thread_id,
        approved=request.approved,
        replacement_message=request.replacement_message,
    )
    return to_response(result)
