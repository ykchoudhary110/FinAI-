from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from finai.catalog import by_code, CATALOG, DATASET_VERSION


def money(value) -> float:
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


@dataclass
class GstRateResult:
    code: str
    name: str
    rate: float
    cgst: float
    sgst: float
    igst: float
    cess_rate: float
    itc_eligible: bool
    rcm_applicable: bool
    blocked_reason: str
    source_notification: str
    effective_from: str
    effective_to: str | None
    dataset_version: str
    is_valid_for_date: bool


def resolve_rate(code: str, transaction_date: str | None = None, is_interstate: bool = False) -> GstRateResult:
    """
    Resolve GST rate for a given HSN/SAC code.
    - Validates the code exists in the master catalog
    - Checks the transaction date falls within effective_from / effective_to
    - Computes CGST/SGST (50/50) or IGST based on interstate flag
    - Raises ValueError for unknown codes
    """
    # Find in catalog
    item = by_code(code.strip())
    if item is None:
        # Try prefix match (e.g. 84716040 matches under 8471)
        for candidate in CATALOG:
            if code.startswith(candidate["code"]) or candidate["code"].startswith(code):
                item = candidate
                break
    if item is None:
        raise ValueError(f"Unrecognized HSN/SAC code: {code}. Cannot determine rate.")
    
    # Parse and validate date
    is_valid_for_date = True
    if transaction_date:
        # Parse YYYY-MM-DD or DD/MM/YYYY
        try:
            if "/" in transaction_date:
                parts = transaction_date.split("/")
                tx_date = date(int(parts[2]), int(parts[1]), int(parts[0]))
            else:
                tx_date = date.fromisoformat(transaction_date)
        except (ValueError, IndexError):
            tx_date = date.today()
        
        eff_from = date.fromisoformat(item["effective_from"])
        if tx_date < eff_from:
            is_valid_for_date = False
        if item.get("effective_to"):
            eff_to = date.fromisoformat(item["effective_to"])
            if tx_date > eff_to:
                is_valid_for_date = False
    
    rate = item["rate"]
    if is_interstate:
        cgst_rate, sgst_rate, igst_rate = 0.0, 0.0, rate
    else:
        half = money(rate / 2)
        cgst_rate, sgst_rate, igst_rate = half, half, 0.0
    
    return GstRateResult(
        code=item["code"],
        name=item["name"],
        rate=rate,
        cgst=cgst_rate,
        sgst=sgst_rate,
        igst=igst_rate,
        cess_rate=item.get("cess_rate", 0.0),
        itc_eligible=item["itc"],
        rcm_applicable=item.get("rcm_applicable", False),
        blocked_reason=item.get("blocked_reason", ""),
        source_notification=item["source"],
        effective_from=item["effective_from"],
        effective_to=item.get("effective_to"),
        dataset_version=DATASET_VERSION,
        is_valid_for_date=is_valid_for_date,
    )
