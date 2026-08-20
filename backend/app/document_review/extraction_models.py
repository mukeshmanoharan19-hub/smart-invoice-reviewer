"""Wire models for OpenAI strict structured extraction output.

All money and date values are strings because the Responses API strict schema
does not support Decimal or date. Deterministic code in normalize.py parses them.
Document kind is decided by the classification pipeline step before extraction.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class WireConfidenceString(BaseModel):
    value: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


class WireMoney(BaseModel):
    amount: str | None = None
    currency_code: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


class WireAddress(BaseModel):
    content: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country_region: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


class WireLineItem(BaseModel):
    description: str | None = None
    quantity: str | None = None
    unit_price: str | None = None
    amount: str | None = None
    tax: str | None = None


class WireTaxDetail(BaseModel):
    description: str | None = None
    rate: str | None = None
    amount: str | None = None


class DocumentExtractionWire(BaseModel):
    """Field extraction for a document whose kind is already classified."""

    document_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    vendor_name: WireConfidenceString | None = None
    vendor_address: WireAddress | None = None
    vendor_tax_id: WireConfidenceString | None = None

    customer_name: WireConfidenceString | None = None
    customer_address: WireAddress | None = None
    customer_tax_id: WireConfidenceString | None = None

    invoice_id: WireConfidenceString | None = None
    invoice_date: WireConfidenceString | None = None
    due_date: WireConfidenceString | None = None
    purchase_order: WireConfidenceString | None = None
    transaction_date: WireConfidenceString | None = None
    receipt_type: WireConfidenceString | None = None

    subtotal: WireMoney | None = None
    total_tax: WireMoney | None = None
    total: WireMoney | None = None
    amount_due: WireMoney | None = None

    items: list[WireLineItem] = Field(default_factory=list)
    tax_details: list[WireTaxDetail] = Field(default_factory=list)
