from __future__ import annotations

import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

AUDIT_DB = Path("backend/var/readiness.db")


@dataclass
class Verdict:
    allowed: bool
    reason: str
    audit_id: Optional[str] = None


def _audit(tenant_id: str, requested_tenant: str, deal_id: str, reason: str) -> str:
    AUDIT_DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(AUDIT_DB)
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_log (
          audit_id TEXT PRIMARY KEY,
          tenant_id TEXT,
          requested_tenant_id TEXT,
          deal_id TEXT,
          reason TEXT,
          ts TEXT
        )
        """
    )
    audit_id = str(uuid.uuid4())
    con.execute(
        "INSERT INTO audit_log (audit_id, tenant_id, requested_tenant_id, deal_id, reason, ts) VALUES (?, ?, ?, ?, ?, ?)",
        (audit_id, tenant_id, requested_tenant, deal_id, reason, datetime.now(timezone.utc).isoformat()),
    )
    con.commit()
    con.close()
    return audit_id


def jurisdiction_trap(question: str) -> bool:
    text = (question or "").lower()
    markers = ("abu dhabi", "aldar", "modon")
    return any(marker in text for marker in markers)


def check_scope(tenant_id: str, deal: dict | None, requested_tenant: str | None, question: str | None) -> Verdict:
    requested = requested_tenant or tenant_id
    deal_id = (deal or {}).get("deal_id", "")
    if not tenant_id:
        audit_id = _audit(tenant_id, requested, deal_id, "missing_tenant")
        return Verdict(False, "missing_tenant", audit_id)
    if requested != tenant_id or (deal and deal.get("tenant_id") != tenant_id):
        audit_id = _audit(tenant_id, requested, deal_id, "cross_tenant")
        return Verdict(False, "cross_tenant", audit_id)
    if jurisdiction_trap(question or ""):
        _audit(tenant_id, requested, deal_id, "jurisdiction_review")
    return Verdict(True, "in_scope")
