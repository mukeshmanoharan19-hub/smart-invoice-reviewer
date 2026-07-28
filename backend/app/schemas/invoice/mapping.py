"""Map Document Intelligence invoice fields into the Invoice schema."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.schemas.field_readers import (
    FieldMap,
    read_address,
    read_array,
    read_date,
    read_money,
    read_number,
    read_string,
    read_tax_details,
)
from app.schemas.invoice.model import Invoice, InvoiceLineItem


def _object(item: FieldMap) -> FieldMap:
    value = item.get("valueObject")
    return value if isinstance(value, Mapping) else {}


def map_invoice_fields(
    fields: Mapping[str, Any],
    *,
    document_confidence: float | None = None,
) -> Invoice:
    items: list[InvoiceLineItem] = []
    for item in read_array(fields, "Items"):
        obj = _object(item)
        items.append(
            InvoiceLineItem(
                description=read_string(obj, "Description"),
                quantity=read_number(obj, "Quantity"),
                unit=read_string(obj, "Unit"),
                unit_price=read_money(obj, "UnitPrice"),
                amount=read_money(obj, "Amount"),
                tax=read_money(obj, "Tax"),
                tax_rate=read_string(obj, "TaxRate"),
                product_code=read_string(obj, "ProductCode"),
                date=read_date(obj, "Date"),
            )
        )

    return Invoice(
        vendor_name=read_string(fields, "VendorName"),
        vendor_address=read_address(fields, "VendorAddress"),
        vendor_tax_id=read_string(fields, "VendorTaxId"),
        customer_name=read_string(fields, "CustomerName"),
        customer_address=read_address(fields, "CustomerAddress"),
        customer_tax_id=read_string(fields, "CustomerTaxId"),
        invoice_id=read_string(fields, "InvoiceId"),
        invoice_date=read_date(fields, "InvoiceDate"),
        due_date=read_date(fields, "DueDate"),
        purchase_order=read_string(fields, "PurchaseOrder"),
        subtotal=read_money(fields, "SubTotal"),
        total_tax=read_money(fields, "TotalTax"),
        invoice_total=read_money(fields, "InvoiceTotal"),
        amount_due=read_money(fields, "AmountDue"),
        items=items,
        tax_details=read_tax_details(fields),
        document_confidence=document_confidence,
    )
