"""Provider-independent document extraction schemas."""

from app.schemas.invoice import Invoice, InvoiceLineItem, map_invoice_fields
from app.schemas.receipt import Receipt, ReceiptLineItem, ReceiptPayment, map_receipt_fields

__all__ = [
    "Invoice",
    "InvoiceLineItem",
    "Receipt",
    "ReceiptLineItem",
    "ReceiptPayment",
    "map_invoice_fields",
    "map_receipt_fields",
]
