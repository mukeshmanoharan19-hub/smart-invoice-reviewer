"""Deterministic conversion from OpenAI wire strings to typed review fields."""

from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Literal

from app.document_review.extraction_models import (
    DocumentExtractionWire,
    WireAddress,
    WireConfidenceString,
    WireMoney,
)
from app.document_review.review_fields import ReviewFields, ReviewLineItem


class NormalizationError(ValueError):
    """Raised when a wire value cannot be parsed into a typed field."""


def _parse_decimal(raw: str | None, field_name: str) -> Decimal | None:
    if raw is None:
        return None
    text = raw.strip().replace(",", "")
    if not text:
        return None
    try:
        return Decimal(text)
    except InvalidOperation as exc:
        raise NormalizationError(f"Invalid decimal for {field_name}: {raw!r}") from exc


def _parse_date(raw: str | None, field_name: str) -> date | None:
    if raw is None:
        return None
    text = raw.strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError as exc:
        raise NormalizationError(f"Invalid date for {field_name}: {raw!r}") from exc


def _string_value(field: WireConfidenceString | None) -> str | None:
    if field is None or field.value is None:
        return None
    text = field.value.strip()
    return text or None


def _confidence(field: WireConfidenceString | WireMoney | WireAddress | None) -> float | None:
    if field is None:
        return None
    return field.confidence


def _money_amount(field: WireMoney | None, field_name: str) -> Decimal | None:
    if field is None:
        return None
    return _parse_decimal(field.amount, field_name)


def _money_currency(field: WireMoney | None) -> str | None:
    if field is None or field.currency_code is None:
        return None
    text = field.currency_code.strip().upper()
    return text or None


def _address_content(field: WireAddress | None) -> str | None:
    if field is None:
        return None
    parts = [
        field.content,
        field.city,
        field.state,
        field.postal_code,
        field.country_region,
    ]
    joined = ", ".join(part.strip() for part in parts if part and part.strip())
    return joined or None


def normalize_extraction(
    wire: DocumentExtractionWire,
    *,
    document_type: Literal["invoice", "receipt"],
    classification_confidence: float | None = None,
) -> ReviewFields:
    """Parse wire strings into provider-independent review fields."""

    currencies = [
        _money_currency(wire.subtotal),
        _money_currency(wire.total_tax),
        _money_currency(wire.total),
        _money_currency(wire.amount_due),
    ]
    currency = next((code for code in currencies if code), None)

    invoice_date = _parse_date(_string_value(wire.invoice_date), "invoice_date")
    transaction_date = _parse_date(_string_value(wire.transaction_date), "transaction_date")
    due_date = _parse_date(_string_value(wire.due_date), "due_date")

    # Receipts often only expose a transaction date; invoices use invoice_date.
    primary_date = invoice_date or transaction_date

    line_items: list[ReviewLineItem] = []
    for index, item in enumerate(wire.items):
        line_items.append(
            ReviewLineItem(
                description=(item.description or "").strip() or None,
                quantity=_parse_decimal(item.quantity, f"items[{index}].quantity"),
                unit_price=_parse_decimal(item.unit_price, f"items[{index}].unit_price"),
                amount=_parse_decimal(item.amount, f"items[{index}].amount"),
                tax=_parse_decimal(item.tax, f"items[{index}].tax"),
            )
        )

    document_confidence = wire.document_confidence
    if document_confidence is None:
        document_confidence = classification_confidence

    return ReviewFields(
        document_type=document_type,
        vendor_name=_string_value(wire.vendor_name),
        vendor_name_confidence=_confidence(wire.vendor_name),
        vendor_gstin=_string_value(wire.vendor_tax_id),
        vendor_gstin_confidence=_confidence(wire.vendor_tax_id),
        vendor_address=_address_content(wire.vendor_address),
        customer_name=_string_value(wire.customer_name),
        customer_name_confidence=_confidence(wire.customer_name),
        customer_gstin=_string_value(wire.customer_tax_id),
        customer_gstin_confidence=_confidence(wire.customer_tax_id),
        customer_address=_address_content(wire.customer_address),
        invoice_number=_string_value(wire.invoice_id),
        invoice_number_confidence=_confidence(wire.invoice_id),
        invoice_date=primary_date,
        invoice_date_confidence=(
            _confidence(wire.invoice_date) or _confidence(wire.transaction_date)
        ),
        due_date=due_date,
        due_date_confidence=_confidence(wire.due_date),
        purchase_order=_string_value(wire.purchase_order),
        purchase_order_confidence=_confidence(wire.purchase_order),
        currency=currency,
        subtotal=_money_amount(wire.subtotal, "subtotal"),
        subtotal_confidence=_confidence(wire.subtotal),
        total_tax=_money_amount(wire.total_tax, "total_tax"),
        total_tax_confidence=_confidence(wire.total_tax),
        total=_money_amount(wire.total, "total"),
        total_confidence=_confidence(wire.total),
        document_confidence=document_confidence,
        line_items=line_items,
    )
