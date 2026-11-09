"""Canal Courtyard: the critic blocks a fair price when the project has stalled."""

from agent.runner import run_deal


def test_critic_blocks_a_fair_price_on_a_stalled_project():
    state = run_deal("tenant_sandstone", "deal_canal_courtyard")

    assert state["refused"] is False
    assert state["live_dld_check"] is False

    valuation = next(item for item in state["findings"] if item["agent"] == "valuation")
    offplan = next(item for item in state["findings"] if item["agent"] == "offplan")
    permit = next(item for item in state["findings"] if item["agent"] == "permit")

    assert valuation["within_comparables"] is True
    assert offplan["stalled"] is True
    assert offplan["handover_conflict"] is True
    assert permit["beneficiary_mismatch"] is True
    assert permit["live_dld_check"] is False

    assert state["repair_attempts"] == 1
    codes = {item["code"] for item in state["critic"]["conflicts"]}
    assert "stalled_price" in codes
    assert "handover_dates" in codes
    assert "beneficiary_mismatch" in codes
    assert state["critic"]["blocks_fair_price"] is True

    draft = state["draft"]
    assert draft["price_is_fair"] is False
    assert draft["sent_to_buyer"] is False
    assert draft["payment_approved"] is False
    text = draft["text"].lower()
    assert "the price is fair" not in text
    assert "does not call the price fair" in text
    assert "no live dld check" in text
    assert "nothing in this report is sent to a buyer" in text
    cited = set(draft["citations"])
    assert {"doc:comparables", "doc:status", "doc:brochure", "doc:spa"} <= cited

    documents = {item["id"]: item for item in state["documents"]}
    for item in documents.values():
        assert item["banner"] == "SYNTHETIC DEMO"
    assert documents["doc:status"]["issuer_label"] == "NOT ISSUED BY DLD"
