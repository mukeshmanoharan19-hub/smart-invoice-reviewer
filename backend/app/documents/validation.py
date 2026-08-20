"""Pure Northstar invoice and receipt policy rules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from stdnum.in_ import gstin as gstin_mod

from app.config import AppConfig, get_app_config
from app.document_review.review_fields import ReviewFields

Severity = Literal["error", "warning"]


@dataclass(frozen=True, slots=True)
class Issue:
    code: str
    severity: Severity
    message: str
    field: str | None = None


def validate_document(
    fields: ReviewFields,
    *,
    duplicate_exists: bool = False,
    selected_gl_code: str | None = None,
    config: AppConfig | None = None,
) -> list[Issue]:
    cfg = config or get_app_config()
    if fields.document_type == "receipt":
        issues = _validate_receipt(fields, cfg)
    else:
        issues = _validate_invoice(fields, cfg, duplicate_exists=duplicate_exists)

    if not selected_gl_code:
        issues.append(
            Issue(
                code="gl_account_required",
                severity="error",
                message="Select a Northstar GL account before approval",
                field="gl_account_code",
            )
        )
    return issues


def has_blocking_errors(issues: list[Issue]) -> bool:
    return any(issue.severity == "error" for issue in issues)


def _validate_invoice(
    fields: ReviewFields,
    cfg: AppConfig,
    *,
    duplicate_exists: bool,
) -> list[Issue]:
    issues: list[Issue] = []

    if not fields.vendor_name:
        issues.append(
            Issue("vendor_name_required", "error", "Vendor name is required", "vendor_name")
        )
    if not fields.customer_name:
        issues.append(
            Issue(
                "customer_name_required",
                "error",
                "Customer name is required",
                "customer_name",
            )
        )

    issues.extend(_gstin_issues(fields.vendor_gstin, role="vendor", required=True))
    issues.extend(_customer_gstin_issues(fields.customer_gstin, cfg))

    if not fields.invoice_number:
        issues.append(
            Issue(
                "invoice_number_required",
                "error",
                "Invoice number is required",
                "invoice_number",
            )
        )
    if fields.invoice_date is None:
        issues.append(
            Issue("invoice_date_required", "error", "Invoice date is required", "invoice_date")
        )
    if fields.total is None:
        issues.append(Issue("total_required", "error", "Invoice total is required", "total"))
    elif fields.total <= 0:
        issues.append(
            Issue("total_not_positive", "error", "Invoice total must be positive", "total")
        )

    if not fields.currency:
        issues.append(Issue("currency_required", "error", "Currency is required", "currency"))
    elif fields.currency != cfg.expected_currency:
        issues.append(
            Issue(
                "currency_unexpected",
                "error",
                f"Expected currency {cfg.expected_currency}",
                "currency",
            )
        )

    if (
        fields.invoice_date is not None
        and fields.due_date is not None
        and fields.due_date < fields.invoice_date
    ):
        issues.append(
            Issue(
                "due_date_before_invoice_date",
                "error",
                "Due date cannot be before invoice date",
                "due_date",
            )
        )

    issues.extend(_total_reconciliation(fields, cfg, mismatch_code="invoice_total_mismatch"))

    if not fields.purchase_order:
        issues.append(
            Issue(
                "purchase_order_missing",
                "warning",
                "Purchase order is missing",
                "purchase_order",
            )
        )

    if duplicate_exists:
        issues.append(
            Issue(
                "duplicate_invoice",
                "error",
                "An invoice with this vendor and invoice number already exists",
                "invoice_number",
            )
        )

    issues.extend(_low_confidence_warning(fields, cfg))
    return issues


def _validate_receipt(fields: ReviewFields, cfg: AppConfig) -> list[Issue]:
    issues: list[Issue] = []

    if not fields.vendor_name:
        issues.append(
            Issue("merchant_name_required", "error", "Merchant name is required", "vendor_name")
        )
    if fields.invoice_date is None:
        issues.append(
            Issue(
                "transaction_date_required",
                "error",
                "Transaction date is required",
                "invoice_date",
            )
        )
    if fields.total is None:
        issues.append(Issue("total_required", "error", "Receipt total is required", "total"))
    elif fields.total <= 0:
        issues.append(
            Issue("total_not_positive", "error", "Receipt total must be positive", "total")
        )

    if not fields.currency:
        issues.append(Issue("currency_required", "error", "Currency is required", "currency"))
    elif fields.currency != cfg.expected_currency:
        issues.append(
            Issue(
                "currency_unexpected",
                "error",
                f"Expected currency {cfg.expected_currency}",
                "currency",
            )
        )

    if fields.total_tax is None:
        issues.append(
            Issue("total_tax_required", "error", "Receipt tax total is required", "total_tax")
        )

    issues.extend(_total_reconciliation(fields, cfg, mismatch_code="receipt_total_mismatch"))
    issues.extend(_low_confidence_warning(fields, cfg))
    return issues


def _gstin_issues(value: str | None, *, role: str, required: bool) -> list[Issue]:
    label = f"{role}_gstin"
    if not value:
        if required:
            return [
                Issue(
                    f"{label}_required",
                    "error",
                    f"{role.capitalize()} GSTIN is required",
                    label,
                )
            ]
        return []
    if not gstin_mod.is_valid(value):
        return [
            Issue(
                f"{label}_invalid",
                "error",
                f"{role.capitalize()} GSTIN failed structure or checksum validation",
                label,
            )
        ]
    return []


def _customer_gstin_issues(value: str | None, cfg: AppConfig) -> list[Issue]:
    if not value:
        return [
            Issue(
                "customer_gstin_required",
                "error",
                "Customer GSTIN is required",
                "customer_gstin",
            )
        ]
    if not gstin_mod.is_valid(value):
        return [
            Issue(
                "customer_gstin_invalid",
                "error",
                "Customer GSTIN failed structure or checksum validation",
                "customer_gstin",
            )
        ]
    if value != cfg.northstar_customer_gstin:
        return [
            Issue(
                "customer_gstin_mismatch",
                "error",
                f"Customer GSTIN must be Northstar {cfg.northstar_customer_gstin}",
                "customer_gstin",
            )
        ]
    return []


def _total_reconciliation(
    fields: ReviewFields,
    cfg: AppConfig,
    *,
    mismatch_code: str,
) -> list[Issue]:
    if fields.subtotal is None or fields.total_tax is None or fields.total is None:
        return []
    expected = fields.subtotal + fields.total_tax
    if abs(expected - fields.total) > cfg.amount_tolerance:
        return [
            Issue(
                mismatch_code,
                "error",
                (
                    f"Subtotal ({fields.subtotal}) + tax ({fields.total_tax}) "
                    f"does not equal total ({fields.total})"
                ),
                "total",
            )
        ]
    return []


def _low_confidence_warning(fields: ReviewFields, cfg: AppConfig) -> list[Issue]:
    # Human corrections outrank model confidence for the prepared review.
    if any(source == "human" for source in fields.field_sources.values()):
        return []
    confidence = fields.document_confidence
    if confidence is not None and confidence < cfg.low_confidence_threshold:
        return [
            Issue(
                "low_extraction_confidence",
                "warning",
                (
                    f"Self-reported extraction confidence {confidence:.2f} "
                    f"is below {cfg.low_confidence_threshold:.2f}"
                ),
                "document_confidence",
            )
        ]
    return []

