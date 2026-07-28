"""Invoice extraction schema."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.common import Address, ConfidenceField, MoneyAmount, TaxDetail


class InvoiceLineItem(BaseModel):
    description: ConfidenceField[str] | None = None
    quantity: ConfidenceField[Decimal] | None = None
    unit: ConfidenceField[str] | None = None
    unit_price: ConfidenceField[MoneyAmount] | None = None
    amount: ConfidenceField[MoneyAmount] | None = None
    tax: ConfidenceField[MoneyAmount] | None = None
    tax_rate: ConfidenceField[str] | None = None
    product_code: ConfidenceField[str] | None = None
    date: ConfidenceField[date] | None = None


class Invoice(BaseModel):
    vendor_name: ConfidenceField[str] | None = None
    vendor_address: ConfidenceField[Address] | None = None
    vendor_tax_id: ConfidenceField[str] | None = None
    customer_name: ConfidenceField[str] | None = None
    customer_address: ConfidenceField[Address] | None = None
    customer_tax_id: ConfidenceField[str] | None = None
    invoice_id: ConfidenceField[str] | None = None
    invoice_date: ConfidenceField[date] | None = None
    due_date: ConfidenceField[date] | None = None
    purchase_order: ConfidenceField[str] | None = None
    subtotal: ConfidenceField[MoneyAmount] | None = None
    total_tax: ConfidenceField[MoneyAmount] | None = None
    invoice_total: ConfidenceField[MoneyAmount] | None = None
    amount_due: ConfidenceField[MoneyAmount] | None = None
    items: list[InvoiceLineItem] = Field(default_factory=list)
    tax_details: list[TaxDetail] = Field(default_factory=list)
    document_confidence: float | None = None
