"""One readable line per agent step, for the desk log."""
from __future__ import annotations

from typing import Any, Dict

_AGENTS = {
    "permit": "Permit verifier",
    "valuation": "Valuation analyst",
    "cost": "Cost modeller",
    "offplan": "Off plan risk analyst",
    "jurisdiction": "Jurisdiction reviewer",
}


def describe(event: Dict[str, Any]) -> str:
    phase = event.get("phase")
    if phase == "graph":
        tool = "LangGraph" if event.get("tool") == "langgraph" else "The runner"
        return f"{tool} opened the file. The nodes are planner, specialists, critic, and deal writer."
    if phase == "planner" and event.get("refused"):
        reason = str(event["refused"])
        if reason == "cross_tenant":
            return "Planner stopped the run. The file belongs to another brokerage, so no findings were read."
        return f"Planner stopped the run. Reason: {reason.replace('_', ' ')}."
    if phase == "planner" and event.get("checklist"):
        names = event.get("checklist") if isinstance(event.get("checklist"), list) else []
        if "jurisdiction" in names:
            return "Planner assigned permit, valuation, cost, off plan risk, and a jurisdiction reviewer."
        return "Planner assigned permit, valuation, cost, and off plan risk."
    if phase == "planner" and event.get("verdict"):
        verdict = str(event["verdict"]).replace("_", " ")
        if verdict == "in scope":
            return "Planner kept the request inside Sandstone Realty."
        return f"Planner refused the request. Reason: {verdict}."
    if phase == "specialist":
        name = _AGENTS.get(str(event.get("agent")), str(event.get("agent") or "Specialist"))
        detail = str(event.get("detail") or "").strip()
        if detail:
            return f"{name}. {detail}"
        return f"{name} returned a cited finding."
    if phase == "critic":
        detail = str(event.get("detail") or "").strip()
        if detail:
            return f"Critic. {detail}"
        codes = event.get("conflicts") if isinstance(event.get("conflicts"), list) else []
        if not codes:
            return "Critic found no conflict across the findings."
        readable = ", ".join(str(code).replace("_", " ") for code in codes)
        return f"Critic raised {readable}."
    if phase == "repair":
        return "One repair read the same documents again. The conflict remains."
    if phase == "writer":
        model = str(event.get("model") or "template")
        if event.get("fallback_reason"):
            requested = str(event.get("requested_model") or "the selected model")
            fair = "called the price fair" if event.get("price_is_fair") else "does not call the price fair"
            reason = str(event.get("fallback_reason"))
            if "not accessible" in reason or "unsupported_api" in reason:
                return (
                    f"{requested} cannot be called on chat completions. "
                    f"The template was used instead and {fair}."
                )
            return f"OmniRoute did not answer for {requested}. The template was used instead and {fair}."
        fair = "called the price fair" if event.get("price_is_fair") else "does not call the price fair"
        usage = event.get("usage") if isinstance(event.get("usage"), dict) else {}
        if model != "template" and usage:
            prompt = int(usage.get("prompt_tokens") or 0)
            completion = int(usage.get("completion_tokens") or 0)
            return (
                f"Deal writer called OmniRoute model {model}. "
                f"{prompt} prompt tokens, {completion} completion tokens. It {fair}."
            )
        return f"Deal writer used {model} and {fair}. Nothing is sent to a buyer."
    return "The runner recorded a step."
