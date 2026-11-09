from __future__ import annotations

import re
from typing import Any, Callable, Dict, List, Optional, TypedDict

from . import corpus, llm, scope
from .console import describe

try:
    from langgraph.graph import END, START, StateGraph
    _HAS_LANGGRAPH = True
except Exception:
    _HAS_LANGGRAPH = False
    START = "__start__"
    END = "__end__"


class DealState(TypedDict, total=False):
    tenant_id: str
    deal_id: str
    requested_tenant: str
    question: str
    refused: bool
    refusal_reason: str
    live_dld_check: bool
    documents: List[Dict[str, Any]]
    findings: List[Dict[str, Any]]
    repair_attempts: int
    repair_note: str
    critic: Dict[str, Any]
    draft: Dict[str, Any]
    steps: List[Dict[str, Any]]


def _section(deal: Dict[str, Any], doc_id: str, name: str) -> str:
    for doc in deal["documents"]:
        if doc["id"] == doc_id:
            return str(doc["sections"][name])
    raise KeyError(doc_id)


def _permit(deal: Dict[str, Any]) -> Dict[str, Any]:
    brochure_ref = _section(deal, "doc:brochure", "beneficiary")
    spa_ref = _section(deal, "doc:spa", "beneficiary")
    schedule_unit = _section(deal, "doc:schedule", "unit")
    return {
        "agent": "permit",
        "live_dld_check": False,
        "beneficiary_mismatch": brochure_ref != spa_ref,
        "unit_mismatch": deal["unit_id"] not in schedule_unit,
        "project": deal["project"],
        "developer": deal["developer"],
        "broker_status": "to verify",
        "manual_links": corpus.OFFICIAL_LINKS,
        "citations": ["doc:brochure", "doc:spa", "doc:schedule", "doc:status"],
        "note": "Identity was compared across the seeded documents. No official service was queried.",
    }


def _valuation(deal: Dict[str, Any]) -> Dict[str, Any]:
    prices = next(doc["prices_aed"] for doc in deal["documents"] if doc["id"] == "doc:comparables")
    low, high = min(prices), max(prices)
    asking = int(deal["asking_price_aed"])
    return {
        "agent": "valuation",
        "within_comparables": low <= asking <= high,
        "asking_price_aed": asking,
        "low_aed": low,
        "high_aed": high,
        "citations": ["doc:brochure", "doc:comparables"],
        "note": "The comparables are seeded sales for a progressing project.",
    }


def _cost(deal: Dict[str, Any]) -> Dict[str, Any]:
    price = int(deal["asking_price_aed"])
    return {
        "agent": "cost",
        "assumptions": True,
        "lines": [
            {"name": "Asking price", "aed": price, "basis": "Brochure figure"},
            {"name": "DLD fee assumption", "aed": round(price * 0.04), "basis": "4 percent assumption, to verify"},
            {"name": "Agency fee assumption", "aed": round(price * 0.02), "basis": "2 percent assumption, to verify"},
        ],
        "mortgage": "No mortgage is assumed.",
        "citations": ["doc:brochure", "doc:schedule"],
        "note": "These figures are assumptions for review. They are not a fee invoice and not payment instructions.",
    }


def _offplan(deal: Dict[str, Any]) -> Dict[str, Any]:
    status = _section(deal, "doc:status", "status").lower()
    brochure_handover = _section(deal, "doc:brochure", "handover")
    spa_handover = _section(deal, "doc:spa", "handover")
    return {
        "agent": "offplan",
        "stalled": "stalled" in status,
        "handover_conflict": brochure_handover.strip() != spa_handover.strip(),
        "brochure_handover": brochure_handover,
        "spa_handover": spa_handover,
        "escrow": "absent",
        "citations": ["doc:status", "doc:brochure", "doc:spa"],
        "note": "The status record is simulated. It does not establish completion or a valid escrow.",
    }


def _jurisdiction(deal: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "agent": "jurisdiction",
        "outside_pack": True,
        "note": (
            "This Dubai checklist does not validate an Abu Dhabi Aldar sale. "
            "No Abu Dhabi pack was loaded. No official service was queried."
        ),
        "citations": ["doc:brochure", "doc:status"],
        "project": deal["project"],
    }


def _detail(item: Dict[str, Any]) -> str:
    agent = item.get("agent")
    citations = ", ".join(item.get("citations") or [])
    if agent == "permit":
        beneficiary = "mismatch" if item.get("beneficiary_mismatch") else "match"
        unit = "mismatch" if item.get("unit_mismatch") else "match"
        return f"Beneficiary {beneficiary}. Schedule unit {unit}. Citations: {citations}."
    if agent == "valuation":
        place = "inside" if item.get("within_comparables") else "outside"
        return (
            f"Asking {int(item['asking_price_aed']):,} AED is {place} "
            f"{int(item['low_aed']):,} to {int(item['high_aed']):,} AED. Citations: {citations}."
        )
    if agent == "cost":
        fees = ", ".join(f"{line['name']} {int(line['aed']):,} AED" for line in item.get("lines") or [])
        return f"{fees}. Citations: {citations}."
    if agent == "offplan":
        stalled = "stalled" if item.get("stalled") else "not stalled"
        handover = "conflict" if item.get("handover_conflict") else "match"
        return f"Construction is {stalled}. Handover dates {handover}. Citations: {citations}."
    if agent == "jurisdiction":
        return str(item.get("note") or "")
    return str(item.get("note") or "")


def _specialist_findings(deal: Dict[str, Any], question: str = "") -> List[Dict[str, Any]]:
    findings = [_permit(deal), _valuation(deal), _cost(deal), _offplan(deal)]
    if scope.jurisdiction_trap(question):
        findings.append(_jurisdiction(deal))
    return findings


def _critic(findings: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_agent = {item["agent"]: item for item in findings}
    conflicts = []
    if by_agent["valuation"]["within_comparables"] and by_agent["offplan"]["stalled"]:
        conflicts.append({
            "code": "stalled_price",
            "detail": "Comparables for a progressing project do not support a fair price for a stalled one.",
        })
    if by_agent["offplan"]["handover_conflict"]:
        conflicts.append({
            "code": "handover_dates",
            "detail": "The brochure states a handover month and the SPA extract makes handover conditional.",
        })
    if by_agent["permit"]["beneficiary_mismatch"]:
        conflicts.append({
            "code": "beneficiary_mismatch",
            "detail": "The brochure and the SPA extract name different beneficiary references. Pay neither.",
        })
    if by_agent["permit"]["unit_mismatch"]:
        conflicts.append({
            "code": "unit_id",
            "detail": "The payment schedule names a different unit from the brochure and the SPA extract.",
        })
    blocks = any(item["code"] == "stalled_price" for item in conflicts)
    return {
        "conflicts": conflicts,
        "blocks_fair_price": blocks,
        "report_allowed": True,
        "clean": not conflicts,
    }


def _citations(findings: List[Dict[str, Any]]) -> List[str]:
    citations = []
    for item in findings:
        for cite in item["citations"]:
            if cite not in citations:
                citations.append(cite)
    return citations


def _outside_pack(findings: List[Dict[str, Any]]) -> bool:
    return any(item.get("agent") == "jurisdiction" and item.get("outside_pack") for item in findings)


def _template_text(deal: Dict[str, Any], findings: List[Dict[str, Any]], price_is_fair: bool) -> str:
    if price_is_fair:
        price_sentence = "The asking price sits inside the seeded comparable range, and this report calls the price fair."
    else:
        price_sentence = (
            "The asking price sits inside the seeded comparable range. "
            "The simulated status record says construction has stalled. "
            "This report does not call the price fair."
        )
    return " ".join([
        f"{deal['project']} unit {deal['unit_id']} is a synthetic off plan deal for {deal['brokerage']}.",
        price_sentence,
        "Open conflicts stay in the warnings. Fee lines are assumptions and are marked to verify.",
        "No live DLD check was made. The status record is labelled not issued by DLD.",
        "Nothing in this report is sent to a buyer.",
        *(
            ["This Dubai checklist does not validate an Abu Dhabi Aldar sale."]
            if _outside_pack(findings) else []
        ),
    ])


def _guard_model_text(text: str, price_is_fair: bool, outside_pack: bool = False) -> str:
    kept = []
    for sentence in re.split(r"(?<=[.!?])\s+", text.strip()):
        lowered = sentence.lower()
        if not price_is_fair and ("the price is fair" in lowered or "priced fairly" in lowered):
            continue
        if outside_pack and "abu dhabi" in lowered and "validat" in lowered and "does not validate" not in lowered:
            continue
        kept.append(sentence)
    text = " ".join(kept).strip()
    if not price_is_fair and "does not call the price fair" not in text.lower():
        text = (text + " This report does not call the price fair.").strip()
    if outside_pack and "does not validate an abu dhabi aldar sale" not in text.lower():
        text = (text + " This Dubai checklist does not validate an Abu Dhabi Aldar sale.").strip()
    if "no live dld check" not in text.lower():
        text += " No live DLD check was made."
    if "nothing in this report is sent to a buyer" not in text.lower():
        text += " Nothing in this report is sent to a buyer."
    return text


def _draft(
    deal: Dict[str, Any],
    findings: List[Dict[str, Any]],
    critic: Dict[str, Any],
    model: str = "template",
    complete: Optional[Callable[..., Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    valuation = next(item for item in findings if item["agent"] == "valuation")
    price_is_fair = bool(valuation["within_comparables"] and not critic["blocks_fair_price"])
    template = _template_text(deal, findings, price_is_fair)
    citations = _citations(findings)
    base = {
        "price_is_fair": price_is_fair,
        "sent_to_buyer": False,
        "payment_approved": False,
        "warnings": critic["conflicts"],
        "citations": citations,
    }
    chosen = (model or "template").strip() or "template"
    if chosen == "template":
        return {**base, "text": template, "model": "template"}
    caller = complete or llm.chat
    messages = [
        {
            "role": "system",
            "content": (
                "Write a short deal readiness note for a synthetic Dubai demo. "
                "Use only the findings in the user message. "
                "Do not invent a live DLD check, a payment, or a message to a buyer. "
                "If price_is_fair is false, do not say the price is fair. "
                "Say that this report does not call the price fair. "
                "If a jurisdiction finding says the sale is outside this pack, "
                "say that this Dubai checklist does not validate an Abu Dhabi Aldar sale."
            ),
        },
        {
            "role": "user",
            "content": str({
                "project": deal["project"],
                "unit_id": deal["unit_id"],
                "price_is_fair": price_is_fair,
                "findings": findings,
                "conflicts": critic["conflicts"],
            }),
        },
    ]
    try:
        result = caller(messages, chosen)
        text = _guard_model_text(str(result.get("content") or ""), price_is_fair, _outside_pack(findings))
        return {
            **base,
            "text": text,
            "model": str(result.get("model") or chosen),
            "provider": "omniroute",
            "usage": result.get("usage") or {},
        }
    except Exception as exc:
        return {
            **base,
            "text": template,
            "model": "template",
            "requested_model": chosen,
            "fallback_reason": str(exc),
        }


def _emit(sink: Optional[Callable[[Dict[str, Any]], None]], event: Dict[str, Any]) -> None:
    if sink:
        sink({**event, "line": event.get("line") or describe(event)})


def run_deal(
    tenant_id: str,
    deal_id: str,
    sink: Optional[Callable[[Dict[str, Any]], None]] = None,
    requested_tenant: str | None = None,
    question: str | None = None,
    model: str | None = None,
    complete: Optional[Callable[..., Dict[str, Any]]] = None,
) -> DealState:
    deal = corpus.get_deal(deal_id)
    chosen = (model or "template").strip() or "template"
    initial: DealState = {
        "tenant_id": tenant_id,
        "deal_id": deal_id,
        "requested_tenant": requested_tenant or tenant_id,
        "question": question or "",
        "refused": False,
        "live_dld_check": False,
        "findings": [],
        "repair_attempts": 0,
        "documents": [],
        "steps": [],
        "model": chosen,
    }

    def planner(state: DealState) -> DealState:
        verdict = scope.check_scope(state["tenant_id"], deal, state.get("requested_tenant"), state.get("question"))
        if not verdict.allowed or deal is None:
            reason = verdict.reason if deal is not None else "unknown_deal"
            _emit(sink, {"phase": "planner", "verdict": reason, "refused": reason})
            return {**state, "refused": True, "refusal_reason": reason, "findings": [], "documents": []}
        checklist = ["permit", "valuation", "cost", "offplan"]
        if scope.jurisdiction_trap(state.get("question") or ""):
            checklist.append("jurisdiction")
        _emit(sink, {"phase": "planner", "verdict": verdict.reason})
        _emit(sink, {"phase": "planner", "checklist": checklist})
        return {**state, "documents": deal["documents"], "live_dld_check": False}

    def specialists(state: DealState) -> DealState:
        if state.get("refused"):
            return state
        findings = _specialist_findings(deal, state.get("question") or "")
        for item in findings:
            _emit(sink, {"phase": "specialist", "agent": item["agent"], "detail": _detail(item)})
        return {**state, "findings": findings}

    def critic(state: DealState) -> DealState:
        if state.get("refused"):
            return state
        report = _critic(state["findings"])
        conflicts = report["conflicts"]
        detail = " ".join(f"{item['code'].replace('_', ' ')}: {item['detail']}" for item in conflicts)
        _emit(sink, {"phase": "critic", "conflicts": [item["code"] for item in conflicts], "detail": detail})
        return {**state, "critic": report}

    def repair(state: DealState) -> DealState:
        note = "The specialists read the same documents again. The conflict remains. No date or price was invented."
        _emit(sink, {"phase": "repair", "attempt": 1, "note": note})
        return {**state, "repair_attempts": 1, "repair_note": note}

    def writer(state: DealState) -> DealState:
        if state.get("refused"):
            return state
        draft = _draft(deal, state["findings"], state["critic"], chosen, complete)
        _emit(sink, {
            "phase": "writer",
            "price_is_fair": draft["price_is_fair"],
            "model": draft["model"],
            "requested_model": draft.get("requested_model"),
            "fallback_reason": draft.get("fallback_reason"),
            "usage": draft.get("usage"),
        })
        return {**state, "draft": draft}

    def after_planner(state: DealState) -> str:
        return "end" if state.get("refused") else "specialists"

    def after_critic(state: DealState) -> str:
        conflicts = (state.get("critic") or {}).get("conflicts") or []
        if conflicts and state.get("repair_attempts", 0) < 1:
            return "repair"
        return "writer"

    _emit(sink, {"phase": "graph", "tool": "langgraph" if _HAS_LANGGRAPH else "sequential"})
    if _HAS_LANGGRAPH:
        graph = StateGraph(DealState)
        graph.add_node("planner", planner)
        graph.add_node("specialists", specialists)
        graph.add_node("critic", critic)
        graph.add_node("repair", repair)
        graph.add_node("writer", writer)
        graph.add_edge(START, "planner")
        graph.add_conditional_edges("planner", after_planner, {"specialists": "specialists", "end": END})
        graph.add_edge("specialists", "critic")
        graph.add_conditional_edges("critic", after_critic, {"repair": "repair", "writer": "writer"})
        graph.add_edge("repair", "writer")
        graph.add_edge("writer", END)
        return graph.compile().invoke(initial)

    state = planner(initial)
    if state.get("refused"):
        return state
    state = specialists(state)
    state = critic(state)
    if after_critic(state) == "repair":
        state = repair(state)
    return writer(state)
