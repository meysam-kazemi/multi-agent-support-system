"""Gradio UI for testing the support workflow."""

from __future__ import annotations

import gradio as gr

from agentic_ai_project.service import SupportWorkflowService, WorkflowResult


_service: SupportWorkflowService | None = None


def get_service() -> SupportWorkflowService:
    global _service
    if _service is None:
        _service = SupportWorkflowService()
    return _service


def _chat_messages(result: WorkflowResult) -> list[dict[str, str]]:
    role_map = {"human": "user", "ai": "assistant"}
    return [
        {"role": role_map.get(message["role"], message["role"]), "content": message["content"]}
        for message in result.messages
    ]


def _status(result: WorkflowResult) -> str:
    metadata = result.metadata
    lines = [
        f"thread_id: {metadata['thread_id']}",
        f"department: {metadata['department'] or '-'}",
        f"sentiment: {metadata['sentiment'] or '-'}",
        f"current_node: {metadata['current_node'] or '-'}",
        f"next_step: {metadata['next_step'] or '-'}",
    ]
    if result.interrupted and result.interrupt:
        lines.append("")
        lines.append(f"human_review: {result.interrupt['reason']}")
        lines.append(result.interrupt["question"])
    return "\n".join(lines)


def submit_message(message: str, user_id: str, thread_id: str):
    if not message.strip():
        return gr.update(), thread_id, "", gr.update(visible=False), gr.update(visible=False)

    service = get_service()
    thread_id = thread_id or service.new_thread_id(user_id or "test-user")
    result = service.run(message.strip(), user_id or "test-user", thread_id)
    review_visible = result.interrupted
    return (
        _chat_messages(result),
        thread_id,
        _status(result),
        gr.update(visible=review_visible),
        gr.update(visible=review_visible, value=""),
    )


def approve_response(thread_id: str):
    result = get_service().resume_human_review(thread_id, approved=True)
    return (
        _chat_messages(result),
        _status(result),
        gr.update(visible=False),
        gr.update(visible=False, value=""),
    )


def replace_response(thread_id: str, replacement: str):
    result = get_service().resume_human_review(
        thread_id,
        approved=False,
        replacement_message=replacement.strip(),
    )
    return (
        _chat_messages(result),
        _status(result),
        gr.update(visible=False),
        gr.update(visible=False, value=""),
    )


def new_conversation(user_id: str):
    return [], get_service().new_thread_id(user_id or "test-user"), "", gr.update(visible=False), gr.update(visible=False, value="")


def build_app() -> gr.Blocks:
    with gr.Blocks(title="Agentic Support Workflow") as app:
        gr.Markdown("# Agentic Support Workflow")
        with gr.Row():
            user_id = gr.Textbox(label="User ID", value="test-user", scale=1)
            thread_id = gr.Textbox(label="Thread ID", scale=2)
            reset = gr.Button("New conversation", variant="secondary")

        chatbot = gr.Chatbot(label="Conversation", height=420)
        message = gr.Textbox(label="Customer message", placeholder="Ask a support question...")
        send = gr.Button("Send", variant="primary")
        status = gr.Textbox(label="Workflow status", lines=7, interactive=False)

        with gr.Group(visible=False) as review_panel:
            gr.Markdown("## Human review")
            replacement = gr.Textbox(
                label="Replacement response",
                lines=4,
                placeholder="Write a human response here, or approve the drafted answer.",
                visible=False,
            )
            with gr.Row():
                approve = gr.Button("Approve drafted response", variant="primary")
                replace = gr.Button("Send replacement response")

        send.click(
            submit_message,
            inputs=[message, user_id, thread_id],
            outputs=[chatbot, thread_id, status, review_panel, replacement],
        ).then(lambda: "", outputs=message)
        message.submit(
            submit_message,
            inputs=[message, user_id, thread_id],
            outputs=[chatbot, thread_id, status, review_panel, replacement],
        ).then(lambda: "", outputs=message)
        approve.click(
            approve_response,
            inputs=[thread_id],
            outputs=[chatbot, status, review_panel, replacement],
        )
        replace.click(
            replace_response,
            inputs=[thread_id, replacement],
            outputs=[chatbot, status, review_panel, replacement],
        )
        reset.click(
            new_conversation,
            inputs=[user_id],
            outputs=[chatbot, thread_id, status, review_panel, replacement],
        )

    return app


def launch() -> None:
    build_app().launch()


if __name__ == "__main__":
    launch()
