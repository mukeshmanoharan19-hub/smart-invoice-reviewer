"""Correction email eligibility and drafting boundaries."""

from app.correction_email.eligibility import (
    SUPPLIER_FIXABLE_CODES,
    is_correction_email_eligible,
    supplier_fixable_issues,
)

__all__ = [
    "SUPPLIER_FIXABLE_CODES",
    "is_correction_email_eligible",
    "supplier_fixable_issues",
]
