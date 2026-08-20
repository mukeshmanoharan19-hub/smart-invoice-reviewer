"""Correction-email eligibility: only supplier-fixable policy issues."""

from __future__ import annotations

from app.documents.validation import Issue

SUPPLIER_FIXABLE_CODES = frozenset(
    {
        "vendor_name_required",
        "merchant_name_required",
        "vendor_gstin_required",
        "vendor_gstin_invalid",
        "customer_gstin_required",
        "customer_gstin_invalid",
        "customer_gstin_mismatch",
        "invoice_number_required",
        "invoice_date_required",
        "transaction_date_required",
        "total_required",
        "total_not_positive",
        "total_tax_required",
        "currency_required",
        "currency_unexpected",
        "due_date_before_invoice_date",
        "invoice_total_mismatch",
        "receipt_total_mismatch",
        "purchase_order_missing",
    }
)


def supplier_fixable_issues(issues: list[Issue]) -> list[Issue]:
    return [issue for issue in issues if issue.code in SUPPLIER_FIXABLE_CODES]


def is_correction_email_eligible(issues: list[Issue]) -> bool:
    return bool(supplier_fixable_issues(issues))
