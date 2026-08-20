"""Field provenance: openai extraction vs human corrections."""

from __future__ import annotations

from typing import Any, Literal

from app.document_review.review_fields import ReviewFields

FieldSource = Literal["openai", "human"]

TRACKED_FIELDS: tuple[str, ...] = (
    "vendor_name",
    "vendor_gstin",
    "vendor_address",
    "customer_name",
    "customer_gstin",
    "customer_address",
    "invoice_number",
    "invoice_date",
    "due_date",
    "purchase_order",
    "currency",
    "subtotal",
    "total_tax",
    "total",
)

_CONFIDENCE_BY_FIELD = {
    "vendor_name": "vendor_name_confidence",
    "vendor_gstin": "vendor_gstin_confidence",
    "customer_name": "customer_name_confidence",
    "customer_gstin": "customer_gstin_confidence",
    "invoice_number": "invoice_number_confidence",
    "invoice_date": "invoice_date_confidence",
    "due_date": "due_date_confidence",
    "purchase_order": "purchase_order_confidence",
    "subtotal": "subtotal_confidence",
    "total_tax": "total_tax_confidence",
    "total": "total_confidence",
}


def stamp_openai_sources(fields: ReviewFields) -> ReviewFields:
    """Mark non-empty extracted fields as coming from OpenAI."""

    sources: dict[str, FieldSource] = dict(fields.field_sources)
    for name in TRACKED_FIELDS:
        value = getattr(fields, name)
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        sources[name] = "openai"
    return fields.model_copy(update={"field_sources": sources})


def apply_human_corrections(current: ReviewFields, incoming: ReviewFields) -> ReviewFields:
    """Merge edits; changed fields become human and lose model confidence."""

    payload: dict[str, Any] = incoming.model_dump(mode="python")
    sources: dict[str, FieldSource] = dict(current.field_sources)

    for name in TRACKED_FIELDS:
        old_value = getattr(current, name)
        new_value = getattr(incoming, name)
        confidence_attr = _CONFIDENCE_BY_FIELD.get(name)
        if old_value != new_value:
            sources[name] = "human"
            if confidence_attr is not None:
                payload[confidence_attr] = None
        elif confidence_attr is not None:
            payload[confidence_attr] = getattr(current, confidence_attr)

    payload["field_sources"] = sources
    payload["document_confidence"] = current.document_confidence
    return ReviewFields.model_validate(payload)


def has_human_corrections(fields: ReviewFields) -> bool:
    return any(source == "human" for source in fields.field_sources.values())
