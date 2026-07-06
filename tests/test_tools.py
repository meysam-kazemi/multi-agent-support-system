from agentic_ai_project.tools import check_subscription_status, process_refund


def test_check_subscription_status_returns_mock_values():
    assert check_subscription_status.invoke({"user_id": "u1"}) == "active"
    assert check_subscription_status.invoke({"user_id": "unknown"}) == "not_found"


def test_process_refund_is_deterministic():
    assert process_refund.invoke({"transaction_id": "tx-100"}) is True
    assert process_refund.invoke({"transaction_id": "tx-123"}) is False
    assert process_refund.invoke({"transaction_id": "missing"}) is False
