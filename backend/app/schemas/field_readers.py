"""Helpers for reading Azure Document Intelligence field dictionaries."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, time
from decimal import Decimal
from typing import Any

from app.schemas.common import Address, ConfidenceField, MoneyAmount, TaxDetail

FieldMap = Mapping[str, Any]


def _as_mapping(value: Any) -> FieldMap | None:
    if isinstance(value, Mapping):
        return value
    return None


def _confidence(field: FieldMap | None) -> float | None:
    if field is None:
        return None
    confidence = field.get("confidence")
    return float(confidence) if confidence is not None else None


def read_string(fields: FieldMap, key: str) -> ConfidenceField[str] | None:
    field = _as_mapping(fields.get(key))
    if field is None:
        return None
    value = field.get("valueString")
    if value is None:
        value = field.get("content")
    if value is None:
        return None
    return ConfidenceField(value=str(value), confidence=_confidence(field))


def read_date(fields: FieldMap, key: str) -> ConfidenceField[date] | None:
    field = _as_mapping(fields.get(key))
    if field is None:
        return None
    value = field.get("valueDate")
    if value is None:
        return None
    if isinstance(value, date):
        parsed = value
    else:
        parsed = date.fromisoformat(str(value)[:10])
    return ConfidenceField(value=parsed, confidence=_confidence(field))


def read_time(fields: FieldMap, key: str) -> ConfidenceField[time] | None:
    field = _as_mapping(fields.get(key))
    if field is None:
        return None
    value = field.get("valueTime")
    if value is None:
        return None
    if isinstance(value, time):
        parsed = value
    else:
        parsed = time.fromisoformat(str(value))
    return ConfidenceField(value=parsed, confidence=_confidence(field))


def read_number(fields: FieldMap, key: str) -> ConfidenceField[Decimal] | None:
    field = _as_mapping(fields.get(key))
    if field is None:
        return None
    value = field.get("valueNumber")
    if value is None:
        return None
    return ConfidenceField(value=Decimal(str(value)), confidence=_confidence(field))


def read_money(fields: FieldMap, key: str) -> ConfidenceField[MoneyAmount] | None:
    field = _as_mapping(fields.get(key))
    if field is None:
        return None
    currency = _as_mapping(field.get("valueCurrency"))
    if currency is None or currency.get("amount") is None:
        return None
    money = MoneyAmount(
        amount=Decimal(str(currency["amount"])),
        currency_code=currency.get("currencyCode"),
        currency_symbol=currency.get("currencySymbol"),
    )
    return ConfidenceField(value=money, confidence=_confidence(field))


def read_address(fields: FieldMap, key: str) -> ConfidenceField[Address] | None:
    field = _as_mapping(fields.get(key))
    if field is None:
        return None
    content = field.get("content")
    value_address = _as_mapping(field.get("valueAddress")) or {}
    if content is None and not value_address:
        return None
    address = Address(
        content=str(content) if content is not None else "",
        house_number=value_address.get("houseNumber"),
        road=value_address.get("road"),
        city=value_address.get("city"),
        state=value_address.get("state"),
        postal_code=value_address.get("postalCode"),
        country_region=value_address.get("countryRegion"),
        street_address=value_address.get("streetAddress"),
    )
    if not address.content and not any(
        [
            address.house_number,
            address.road,
            address.city,
            address.state,
            address.postal_code,
            address.country_region,
            address.street_address,
        ]
    ):
        return None
    return ConfidenceField(value=address, confidence=_confidence(field))


def read_phone(fields: FieldMap, key: str) -> ConfidenceField[str] | None:
    field = _as_mapping(fields.get(key))
    if field is None:
        return None
    value = field.get("valuePhoneNumber")
    if value is None:
        value = field.get("content")
    if value is None:
        return None
    return ConfidenceField(value=str(value), confidence=_confidence(field))


def read_country_region(fields: FieldMap, key: str) -> ConfidenceField[str] | None:
    field = _as_mapping(fields.get(key))
    if field is None:
        return None
    value = field.get("valueCountryRegion")
    if value is None:
        value = field.get("content")
    if value is None:
        return None
    return ConfidenceField(value=str(value), confidence=_confidence(field))


def read_array(fields: FieldMap, key: str) -> list[FieldMap]:
    field = _as_mapping(fields.get(key))
    if field is None:
        return []
    values = field.get("valueArray")
    if not isinstance(values, list):
        return []
    return [item for item in values if isinstance(item, Mapping)]


def read_tax_details(fields: FieldMap, key: str = "TaxDetails") -> list[TaxDetail]:
    details: list[TaxDetail] = []
    for item in read_array(fields, key):
        obj = _as_mapping(item.get("valueObject")) or {}
        rate_field = _as_mapping(obj.get("Rate"))
        rate: ConfidenceField[str] | None = None
        if rate_field is not None:
            if rate_field.get("valueNumber") is not None:
                rate = ConfidenceField(
                    value=str(rate_field["valueNumber"]),
                    confidence=_confidence(rate_field),
                )
            elif rate_field.get("valueString") is not None or rate_field.get("content") is not None:
                rate = ConfidenceField(
                    value=str(rate_field.get("valueString") or rate_field.get("content")),
                    confidence=_confidence(rate_field),
                )
        details.append(
            TaxDetail(
                amount=read_money(obj, "Amount"),
                rate=rate,
                net_amount=read_money(obj, "NetAmount"),
                description=read_string(obj, "Description"),
            )
        )
    return details
