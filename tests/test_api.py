from fastapi.testclient import TestClient

from agentic_ai_project import api
from agentic_ai_project.service import WorkflowResult


class StubService:
    def run(self, user_query: str, user_id: str, thread_id: str | None = None) -> WorkflowResult:
        return WorkflowResult(
            messages=[
                {"role": "human", "content": user_query},
                {"role": "ai", "content": "Mock response"},
            ],
            metadata={
                "thread_id": thread_id or "test-thread",
                "department": "general",
                "sentiment": "neutral",
                "current_node": "sentiment_analyzer",
                "next_step": "done",
            },
        )

    def resume_human_review(
        self,
        thread_id: str,
        approved: bool,
        replacement_message: str = "",
    ) -> WorkflowResult:
        return WorkflowResult(
            messages=[{"role": "ai", "content": replacement_message or "Approved"}],
            metadata={
                "thread_id": thread_id,
                "department": "general",
                "sentiment": "negative",
                "current_node": "human_support",
                "next_step": "done",
            },
        )


def test_health_endpoint():
    client = TestClient(api.app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "agentic-ai-project"}


def test_chat_endpoint_uses_workflow_service(monkeypatch):
    monkeypatch.setattr(api, "get_service", lambda: StubService())
    client = TestClient(api.app)

    response = client.post(
        "/chat",
        json={
            "message": "What can this service do?",
            "user_id": "u1",
            "thread_id": "thread-1",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["messages"][-1] == {"role": "ai", "content": "Mock response"}
    assert body["metadata"]["thread_id"] == "thread-1"
    assert body["interrupted"] is False


def test_resume_requires_replacement_when_not_approved(monkeypatch):
    monkeypatch.setattr(api, "get_service", lambda: StubService())
    client = TestClient(api.app)

    response = client.post(
        "/human-review/resume",
        json={"thread_id": "thread-1", "approved": False},
    )

    assert response.status_code == 400
