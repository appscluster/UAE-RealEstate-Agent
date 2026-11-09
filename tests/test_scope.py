from agent.runner import run_deal


def test_another_brokerage_is_refused_before_findings():
    state = run_deal("tenant_sandstone", "deal_other_broker")
    assert state["refused"] is True
    assert state["refusal_reason"] == "cross_tenant"
    assert state["findings"] == []
    assert state.get("draft") is None


def test_an_abu_dhabi_question_is_answered_by_a_jurisdiction_reviewer():
    lines = []

    def complete(messages, model):
        return {
            "content": "The Dubai checklist validates the Abu Dhabi sale. The price is fair.",
            "model": model,
            "usage": {"prompt_tokens": 4, "completion_tokens": 4},
        }

    state = run_deal(
        "tenant_sandstone",
        "deal_canal_courtyard",
        sink=lines.append,
        question="Can this Dubai checklist validate an Abu Dhabi Aldar sale?",
        model="auto/chat",
        complete=complete,
    )
    assert state["refused"] is False
    assert state["live_dld_check"] is False
    reviewer = next(item for item in state["findings"] if item["agent"] == "jurisdiction")
    assert reviewer["outside_pack"] is True
    assert {"permit", "valuation", "cost", "offplan", "jurisdiction"} <= {item["agent"] for item in state["findings"]}
    draft = state["draft"]["text"].lower()
    assert "this dubai checklist does not validate an abu dhabi aldar sale" in draft
    assert "validates the abu dhabi" not in draft
    assert "the price is fair" not in draft
    assert state["draft"]["sent_to_buyer"] is False
    assert state["draft"]["price_is_fair"] is False
    text = " ".join(item.get("line") or "" for item in lines)
    assert "Jurisdiction reviewer" in text
    assert "specialists were not called" not in text
    assert "another brokerage" not in text
