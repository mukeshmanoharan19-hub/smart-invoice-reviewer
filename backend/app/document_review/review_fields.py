"""Provider-independent editable review fields shared by API and policy."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

FieldSource = Literal["openai", "human"]


class ReviewLineItem(BaseModel):
    description: str | None = None
    quantity: Decimal | None = None
    unit_price: Decimal | None = None
    amount: Decimal | None = None
    tax: Decimal | None = None


class ReviewFields(BaseModel):
    document_type: Literal["invoice", "receipt"]
    vendor_name: str | None = None
    vendor_name_confidence: float | None = None
    vendor_gstin: str | None = None
    vendor_gstin_confidence: float | None = None
    vendor_address: str | None = None
    customer_name: str | None = None
    customer_name_confidence: float | None = None
    customer_gstin: str | None = None
    customer_gstin_confidence: float | None = None
    customer_address: str | None = None
    invoice_number: str | None = None
    invoice_number_confidence: float | None = None
    invoice_date: date | None = None
    invoice_date_confidence: float | None = None
    due_date: date | None = None
    due_date_confidence: float | None = None
    purchase_order: str | None = None
    purchase_order_confidence: float | None = None
    currency: str | None = None
    subtotal: Decimal | None = None
    subtotal_confidence: float | None = None
    total_tax: Decimal | None = None
    total_tax_confidence: float | None = None
    total: Decimal | None = None
    total_confidence: float | None = None
    document_confidence: float | None = None
    field_sources: dict[str, FieldSource] = Field(default_factory=dict)
    line_items: list[ReviewLineItem] = Field(default_factory=list)
