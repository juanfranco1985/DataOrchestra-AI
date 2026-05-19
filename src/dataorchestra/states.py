from __future__ import annotations

from enum import StrEnum


class DiagnosticStatus(StrEnum):
    INTAKE_PENDING = "intake_pending"
    PRIVACY_REVIEW_REQUIRED = "privacy_review_required"
    DATA_FIX_REQUIRED = "data_fix_required"
    READY_FOR_ANALYSIS = "ready_for_analysis"
    ANALYSIS_DONE = "analysis_done"
    PENDING_HUMAN_REVIEW = "pending_human_review"
    APPROVED_FOR_DELIVERY = "approved_for_delivery"
    DELIVERED = "delivered"
    PILOT_CLOSED = "pilot_closed"


FINAL_DELIVERY_STATES = {
    DiagnosticStatus.APPROVED_FOR_DELIVERY,
    DiagnosticStatus.DELIVERED,
}


def can_deliver(status: str) -> bool:
    return DiagnosticStatus(status) in FINAL_DELIVERY_STATES
