from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_desk_copy_and_palette():
    css = (ROOT / "frontend" / "src" / "styles.css").read_text()
    app = (ROOT / "frontend" / "src" / "App.tsx").read_text()
    assert "#0C6B4D" not in css
    assert "#7A2E24" in css
    assert "Source Sans" not in css
    assert "SYNTHETIC DEMO" in app
    assert "Nothing is sent to a buyer" in app
    assert "quiz" not in app.lower()
    assert "arabic" not in app.lower()
    assert 'aria-label="Agent log"' in app
    assert 'id="model"' in app
    assert "readiness-model" in app
    assert "Abu Dhabi Aldar sale" in app
    assert "No findings were read from another brokerage, and a Dubai checklist was not applied outside Dubai." not in app
    assert "generation.current" in app
    assert "load_failed" in app
    assert "accepted for this file" in app
    assert "back with the coordinator" in app
    assert "pod lead" in app
    assert "cannot be called on chat completions" in app
    assert 'className="spin"' in app
    assert "aria-busy" in app
    assert "prefers-reduced-motion" in css
    assert "/api/deals" in app
    assert 'href="/explain"' in app
    explain = (ROOT / "frontend" / "src" / "ExplainPage.tsx").read_text()
    assert "How this meets the assignment" in explain
    assert "The problem" in explain
    assert "The vision" in explain
    assert "Problem solving acumen" in explain
    assert "code first" in explain.lower()
    assert "Who this serves" in explain
    assert "The path" in explain
    assert "The tools" in explain
    assert "OmniRoute" in explain
    assert "Tenant wall" in explain
    assert "quiz" not in explain.lower()
    assert "arabic" not in explain.lower()
    deals = (ROOT / "data" / "deals.json").read_text()
    assert "Creek Lane" in deals
    assert "Palm Walk" in deals
