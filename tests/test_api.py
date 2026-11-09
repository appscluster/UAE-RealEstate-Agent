from fastapi.testclient import TestClient

from backend.app import app

client = TestClient(app)


def test_approve_stores_the_report_and_sends_nothing():
    started = client.post("/api/runs", json={"deal_id": "deal_canal_courtyard"})
    assert started.status_code == 200
    run_id = started.json()["run_id"]

    history = client.get(f"/runs/{run_id}/history").json()["history"]
    seqs = [item["seq"] for item in history]
    assert seqs == list(range(1, len(seqs) + 1))
    assert any(item.get("phase") == "critic" for item in history)

    decision = client.post(
        f"/api/runs/{run_id}/decisions",
        json={"decision": "approve", "actor": "manager:demo"},
    )
    assert decision.status_code == 200
    body = decision.json()
    assert body["record"]["decision"] == "approve"
    assert body["delivery"]["sent"] is False

    report = client.get(f"/api/reports/{body['record']['report_id']}")
    assert report.status_code == 200
    saved = report.json()["report"]
    assert saved["price_is_fair"] is False
    assert saved["sent_to_buyer"] is False
    assert "accepted for this file" in body["delivery"]["note"]

    sent_back = client.post(
        f"/api/runs/{run_id}/decisions",
        json={"decision": "reject", "actor": "manager:demo"},
    )
    assert sent_back.status_code == 200
    assert "back with the coordinator" in sent_back.json()["delivery"]["note"]

    escalated = client.post(
        f"/api/runs/{run_id}/decisions",
        json={"decision": "escalate", "actor": "manager:demo"},
    )
    assert escalated.status_code == 200
    assert "pod lead" in escalated.json()["delivery"]["note"]
    assert escalated.json()["delivery"]["sent"] is False
    latest = client.get(f"/api/runs/{run_id}").json()["run"]
    assert latest["decision"] == "escalate"
