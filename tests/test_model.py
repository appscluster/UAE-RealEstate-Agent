from fastapi.testclient import TestClient

from agent.runner import run_deal
from backend.app import app

client = TestClient(app)


def test_a_chosen_model_writes_the_report_without_calling_a_blocked_price_fair():
    def complete(messages, model):
        assert model == "gh/gpt-6.1-terra"
        assert messages[0]["role"] == "system"
        return {
            "content": "The price is fair. Send the note to the buyer.",
            "model": "gh/gpt-6.1-terra",
            "usage": {"prompt_tokens": 12, "completion_tokens": 8},
        }

    state = run_deal(
        "tenant_sandstone",
        "deal_canal_courtyard",
        model="gh/gpt-6.1-terra",
        complete=complete,
    )
    draft = state["draft"]
    assert draft["model"] == "gh/gpt-6.1-terra"
    assert draft["provider"] == "omniroute"
    assert draft["price_is_fair"] is False
    assert draft["sent_to_buyer"] is False
    assert draft["payment_approved"] is False
    text = draft["text"].lower()
    assert "the price is fair" not in text
    assert "does not call the price fair" in text
    assert draft["usage"]["prompt_tokens"] == 12


def test_a_failed_model_call_keeps_the_template():
    def complete(messages, model):
        raise RuntimeError("gateway down")

    state = run_deal("tenant_sandstone", "deal_canal_courtyard", model="gh/gpt-6.1-sol", complete=complete)
    draft = state["draft"]
    assert draft["model"] == "template"
    assert "gateway down" in draft["fallback_reason"]
    assert "does not call the price fair" in draft["text"].lower()


def test_models_endpoint_names_the_gateway_and_the_template():
    body = client.get("/api/models").json()
    assert "template" in body["models"]
    assert body["default"]
    assert body["gateway"].startswith("http")
    assert "gh/gpt-6.1-sol" not in body["models"]
    assert "gh/gpt-6.1-terra" not in body["models"]
