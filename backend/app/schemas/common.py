"""Shared schema primitives for normalized document fields."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel


class MoneyAmount(BaseModel):
    amount: Decimal
    currency_code: str | None = None
    currency_symbol: str | None = None


class Address(BaseModel):
    content: str
    house_number: str | None = None
    road: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country_region: str | None = None
    street_address: str | None = None


class ConfidenceField[T](BaseModel):
    value: T
    confidence: float | None = None


class TaxDetail(BaseModel):
    amount: ConfidenceField[MoneyAmount] | None = None
    rate: ConfidenceField[str] | None = None
    net_amount: ConfidenceField[MoneyAmount] | None = None
    description: ConfidenceField[str] | None = None
