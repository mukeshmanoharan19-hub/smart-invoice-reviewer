"""Receipt extraction schema."""

from __future__ import annotations

from datetime import date, time
from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.common import Address, ConfidenceField, MoneyAmount, TaxDetail


class ReceiptLineItem(BaseModel):
    description: ConfidenceField[str] | None = None
    quantity: ConfidenceField[Decimal] | None = None
    price: ConfidenceField[MoneyAmount] | None = None
    total_price: ConfidenceField[MoneyAmount] | None = None
    product_code: ConfidenceField[str] | None = None
    quantity_unit: ConfidenceField[str] | None = None


class ReceiptPayment(BaseModel):
    method: ConfidenceField[str] | None = None
    amount: ConfidenceField[MoneyAmount] | None = None


class Receipt(BaseModel):
    merchant_name: ConfidenceField[str] | None = None
    merchant_address: ConfidenceField[Address] | None = None
    merchant_phone_number: ConfidenceField[str] | None = None
    transaction_date: ConfidenceField[date] | None = None
    transaction_time: ConfidenceField[time] | None = None
    subtotal: ConfidenceField[MoneyAmount] | None = None
    total_tax: ConfidenceField[MoneyAmount] | None = None
    total: ConfidenceField[MoneyAmount] | None = None
    tip: ConfidenceField[MoneyAmount] | None = None
    receipt_type: ConfidenceField[str] | None = None
    country_region: ConfidenceField[str] | None = None
    items: list[ReceiptLineItem] = Field(default_factory=list)
    tax_details: list[TaxDetail] = Field(default_factory=list)
    payments: list[ReceiptPayment] = Field(default_factory=list)
    document_confidence: float | None = None
