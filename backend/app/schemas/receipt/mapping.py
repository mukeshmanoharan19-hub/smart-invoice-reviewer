"""Map Document Intelligence receipt fields into the Receipt schema."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.schemas.field_readers import (
    FieldMap,
    read_address,
    read_array,
    read_country_region,
    read_date,
    read_money,
    read_number,
    read_phone,
    read_string,
    read_tax_details,
    read_time,
)
from app.schemas.receipt.model import Receipt, ReceiptLineItem, ReceiptPayment


def _object(item: FieldMap) -> FieldMap:
    value = item.get("valueObject")
    return value if isinstance(value, Mapping) else {}


def map_receipt_fields(
    fields: Mapping[str, Any],
    *,
    document_confidence: float | None = None,
) -> Receipt:
    items: list[ReceiptLineItem] = []
    for item in read_array(fields, "Items"):
        obj = _object(item)
        items.append(
            ReceiptLineItem(
                description=read_string(obj, "Description"),
                quantity=read_number(obj, "Quantity"),
                price=read_money(obj, "Price"),
                total_price=read_money(obj, "TotalPrice"),
                product_code=read_string(obj, "ProductCode"),
                quantity_unit=read_string(obj, "QuantityUnit"),
            )
        )

    payments: list[ReceiptPayment] = []
    for item in read_array(fields, "Payments"):
        obj = _object(item)
        payments.append(
            ReceiptPayment(
                method=read_string(obj, "Method"),
                amount=read_money(obj, "Amount"),
            )
        )

    return Receipt(
        merchant_name=read_string(fields, "MerchantName"),
        merchant_address=read_address(fields, "MerchantAddress"),
        merchant_phone_number=read_phone(fields, "MerchantPhoneNumber"),
        transaction_date=read_date(fields, "TransactionDate"),
        transaction_time=read_time(fields, "TransactionTime"),
        subtotal=read_money(fields, "Subtotal"),
        total_tax=read_money(fields, "TotalTax"),
        total=read_money(fields, "Total"),
        tip=read_money(fields, "Tip"),
        receipt_type=read_string(fields, "ReceiptType"),
        country_region=read_country_region(fields, "CountryRegion"),
        items=items,
        tax_details=read_tax_details(fields),
        payments=payments,
        document_confidence=document_confidence,
    )
