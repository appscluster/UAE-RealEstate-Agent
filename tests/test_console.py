from agent.console import describe
from agent.runner import run_deal


def test_each_agent_step_has_a_console_line():
    lines = []
    run_deal("tenant_sandstone", "deal_canal_courtyard", sink=lines.append)
    text = " ".join(item.get("line") or "" for item in lines)
    assert all(item.get("line") for item in lines)
    assert "Critic" in text
    assert "does not call the price fair" in text
    assert "Beneficiary mismatch" in text
    assert "1,850,000 AED" in text
    assert "doc:brochure" in text


def test_an_unsupported_model_names_the_chat_refusal():
    line = describe({
        "phase": "writer",
        "model": "template",
        "requested_model": "gh/gpt-6.1-sol",
        "fallback_reason": 'model "gpt-6.1-sol" is not accessible via the /chat/completions endpoint',
        "price_is_fair": False,
    })
    assert "gh/gpt-6.1-sol" in line
    assert "cannot be called on chat completions" in line
    assert "template" in line


def test_dummy_files_load_for_the_same_brokerage():
    clean = run_deal("tenant_sandstone", "deal_creek_lane")
    other = run_deal("tenant_sandstone", "deal_palm_walk")
    assert clean["refused"] is False
    assert clean["draft"]["price_is_fair"] is True
    assert clean["live_dld_check"] is False
    assert other["refused"] is False
    assert other["draft"]["price_is_fair"] is False
    assert "stalled_price" in {item["code"] for item in other["critic"]["conflicts"]}
