from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path(__file__).resolve().parents[1]
DEALS_PATH = ROOT / "data" / "deals.json"

OFFICIAL_LINKS = [
    {
        "id": "R1",
        "label": "Dubai REST",
        "url": "https://dubailand.gov.ae/en/eservices/dubai-rest/",
        "note": "Manual link only. This desk does not query it.",
    },
    {
        "id": "R2",
        "label": "Project status enquiry",
        "url": "https://dubailand.gov.ae/en/eservices/real-estate-project-status-landing/real-estate-project-status",
        "note": "Manual link only. This desk does not query it.",
    },
    {
        "id": "R3",
        "label": "RERA ecard verification",
        "url": "https://backoffice.dubailand.gov.ae/en/eservices/validate-e-card-overview/",
        "note": "Manual link only. This desk does not query it.",
    },
]


def load_deals() -> Dict[str, Dict[str, Any]]:
    raw = json.loads(DEALS_PATH.read_text())
    return {item["deal_id"]: item for item in raw["deals"]}


def get_deal(deal_id: str) -> Optional[Dict[str, Any]]:
    return load_deals().get(deal_id)
