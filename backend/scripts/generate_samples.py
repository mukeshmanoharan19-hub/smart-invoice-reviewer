"""Generate the fictional India GSTIN sample corpus and manifest."""

from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from stdnum.in_ import gstin as gstin_mod

ROOT = Path(__file__).resolve().parents[2]
SAMPLES_DIR = ROOT / "samples"
GENERATED_DIR = SAMPLES_DIR / "generated"
MANIFEST_PATH = SAMPLES_DIR / "manifest.json"

CUSTOMER_NAME = "Northstar Facilities Pvt. Ltd."
CUSTOMER_GSTIN = "29AABCN2082N1Z3"
CUSTOMER_ADDRESS = "12 MG Road, Bengaluru, Karnataka 560001"


@dataclass(frozen=True)
class SampleDoc:
    filename: str
    document_type: str
    language: str
    layout: str
    pages: int
    scenario: str
    expected_issue_codes: list[str]
    currency: str
    customer_name: str | None
    customer_gstin: str | None
    due_date: str | None
    invoice_date: str
    invoice_number: str | None
    invoice_total: str
    purchase_order: str | None
    subtotal: str
    total_tax: str
    vendor_name: str
    vendor_gstin: str | None
    line_description: str
    title: str


def _money(value: str) -> Decimal:
    return Decimal(value)


def _assert_valid_gstin(value: str) -> str:
    if not gstin_mod.is_valid(value):
        raise ValueError(f"Invalid GSTIN for corpus: {value}")
    return value


def build_corpus() -> list[SampleDoc]:
    customer = _assert_valid_gstin(CUSTOMER_GSTIN)
    vendors = {
        "bright": _assert_valid_gstin("27AAHCS1234F1ZL"),
        "safai": _assert_valid_gstin("27AAECS4321K1ZB"),
        "chennai": _assert_valid_gstin("33AADCT5678B1ZF"),
        "pune": _assert_valid_gstin("27AAPFU0939F1ZV"),
        "wrong_customer": _assert_valid_gstin("19AABCU9603R1ZK"),
        "lift": _assert_valid_gstin("24AABCU9603R1ZT"),
        "jal": _assert_valid_gstin("07AABCU9603R1ZP"),
        "swachh": _assert_valid_gstin("09AAACH7409R1ZZ"),
        "bharat": _assert_valid_gstin("29AAACW3775F1Z2"),
        "fuel": _assert_valid_gstin("33AABCU9603R1ZU"),
    }
    invalid_vendor = "IN-NOT-A-GSTIN"
    if gstin_mod.is_valid(invalid_vendor):
        raise ValueError("Expected invalid GSTIN to fail validation")

    return [
        SampleDoc(
            filename="01-en-happy-classic.pdf",
            document_type="invoice",
            language="en",
            layout="classic",
            pages=1,
            scenario="happy_path",
            expected_issue_codes=[],
            currency="INR",
            customer_name=CUSTOMER_NAME,
            customer_gstin=customer,
            due_date="2026-07-31",
            invoice_date="2026-07-01",
            invoice_number="EN-2026-1001",
            invoice_total="118.00",
            purchase_order="PO-4001",
            subtotal="100.00",
            total_tax="18.00",
            vendor_name="Bright Spark Electricals Pvt. Ltd.",
            vendor_gstin=vendors["bright"],
            line_description="Electrical maintenance visit",
            title="TAX INVOICE",
        ),
        SampleDoc(
            filename="02-hi-happy-compact.pdf",
            document_type="invoice",
            language="hi",
            layout="compact",
            pages=1,
            scenario="happy_path",
            expected_issue_codes=[],
            currency="INR",
            customer_name=CUSTOMER_NAME,
            customer_gstin=customer,
            due_date="2026-07-31",
            invoice_date="2026-07-01",
            invoice_number="HI-2026-2042",
            invoice_total="283.20",
            purchase_order="PO-4002",
            subtotal="240.00",
            total_tax="43.20",
            vendor_name="Safai Seva Services Pvt. Ltd.",
            vendor_gstin=vendors["safai"],
            line_description="Office cleaning contract - July",
            title="TAX INVOICE / KAR BEEJAK",
        ),
        SampleDoc(
            filename="03-ta-happy-modern.pdf",
            document_type="invoice",
            language="ta",
            layout="modern",
            pages=1,
            scenario="happy_path",
            expected_issue_codes=[],
            currency="INR",
            customer_name=CUSTOMER_NAME,
            customer_gstin=customer,
            due_date="2026-07-31",
            invoice_date="2026-07-01",
            invoice_number="TA-2026-3098",
            invoice_total="531.00",
            purchase_order="PO-4003",
            subtotal="450.00",
            total_tax="81.00",
            vendor_name="Chennai Maintenance Pvt. Ltd.",
            vendor_gstin=vendors["chennai"],
            line_description="HVAC quarterly service",
            title="TAX INVOICE",
        ),
        SampleDoc(
            filename="04-mr-happy-classic.pdf",
            document_type="invoice",
            language="mr",
            layout="classic",
            pages=1,
            scenario="happy_path",
            expected_issue_codes=[],
            currency="INR",
            customer_name=CUSTOMER_NAME,
            customer_gstin=customer,
            due_date="2026-07-31",
            invoice_date="2026-07-01",
            invoice_number="MR-2026-4017",
            invoice_total="212.40",
            purchase_order="PO-4004",
            subtotal="180.00",
            total_tax="32.40",
            vendor_name="Pune Lighting Solutions Pvt. Ltd.",
            vendor_gstin=vendors["pune"],
            line_description="LED fixture replacement",
            title="TAX INVOICE",
        ),
        SampleDoc(
            filename="05-hi-missing-vendor-gstin.pdf",
            document_type="invoice",
            language="hi",
            layout="compact",
            pages=1,
            scenario="missing_vendor_gstin",
            expected_issue_codes=["vendor_gstin_required"],
            currency="INR",
            customer_name=CUSTOMER_NAME,
            customer_gstin=customer,
            due_date="2026-07-31",
            invoice_date="2026-07-01",
            invoice_number="HI-2026-5005",
            invoice_total="377.60",
            purchase_order="PO-4005",
            subtotal="320.00",
            total_tax="57.60",
            vendor_name="Harit Udyan Maintenance Pvt. Ltd.",
            vendor_gstin=None,
            line_description="Garden and grounds upkeep",
            title="TAX INVOICE / KAR BEEJAK",
        ),
        SampleDoc(
            filename="06-ta-invalid-vendor-gstin.pdf",
            document_type="invoice",
            language="ta",
            layout="modern",
            pages=1,
            scenario="invalid_vendor_gstin",
            expected_issue_codes=["vendor_gstin_invalid"],
            currency="INR",
            customer_name=CUSTOMER_NAME,
            customer_gstin=customer,
            due_date="2026-07-31",
            invoice_date="2026-07-01",
            invoice_number="TA-2026-6006",
            invoice_total="106.20",
            purchase_order="PO-4006",
            subtotal="90.00",
            total_tax="16.20",
            vendor_name="Coimbatore Elektro Pvt. Ltd.",
            vendor_gstin=invalid_vendor,
            line_description="Panel inspection",
            title="TAX INVOICE",
        ),
        SampleDoc(
            filename="07-mr-wrong-customer-gstin.pdf",
            document_type="invoice",
            language="mr",
            layout="classic",
            pages=1,
            scenario="wrong_customer_gstin",
            expected_issue_codes=["customer_gstin_mismatch"],
            currency="INR",
            customer_name=CUSTOMER_NAME,
            customer_gstin=vendors["wrong_customer"],
            due_date="2026-07-31",
            invoice_date="2026-07-01",
            invoice_number="MR-2026-7007",
            invoice_total="247.80",
            purchase_order="PO-4007",
            subtotal="210.00",
            total_tax="37.80",
            vendor_name="Swachh Nettoyage India Pvt. Ltd.",
            vendor_gstin=vendors["pune"],
            line_description="Deep cleaning service",
            title="TAX INVOICE",
        ),
        SampleDoc(
            filename="08-en-total-mismatch.pdf",
            document_type="invoice",
            language="en",
            layout="compact",
            pages=1,
            scenario="total_mismatch",
            expected_issue_codes=["invoice_total_mismatch"],
            currency="INR",
            customer_name=CUSTOMER_NAME,
            customer_gstin=customer,
            due_date="2026-07-31",
            invoice_date="2026-07-01",
            invoice_number="EN-2026-8008",
            invoice_total="122.00",
            purchase_order="PO-4008",
            subtotal="100.00",
            total_tax="18.00",
            vendor_name="Lift Safety India Pvt. Ltd.",
            vendor_gstin=vendors["lift"],
            line_description="Lift safety certification",
            title="TAX INVOICE",
        ),
        SampleDoc(
            filename="09-hi-missing-po.pdf",
            document_type="invoice",
            language="hi",
            layout="modern",
            pages=1,
            scenario="missing_purchase_order",
            expected_issue_codes=["purchase_order_missing"],
            currency="INR",
            customer_name=CUSTOMER_NAME,
            customer_gstin=customer,
            due_date="2026-07-31",
            invoice_date="2026-07-01",
            invoice_number="HI-2026-9009",
            invoice_total="165.20",
            purchase_order=None,
            subtotal="140.00",
            total_tax="25.20",
            vendor_name="Jal Karya Plumbing Pvt. Ltd.",
            vendor_gstin=vendors["jal"],
            line_description="Plumbing emergency call-out",
            title="TAX INVOICE / KAR BEEJAK",
        ),
        SampleDoc(
            filename="10-ta-duplicate.pdf",
            document_type="invoice",
            language="ta",
            layout="classic",
            pages=1,
            scenario="duplicate",
            expected_issue_codes=["duplicate_invoice"],
            currency="INR",
            customer_name=CUSTOMER_NAME,
            customer_gstin=customer,
            due_date="2026-07-31",
            invoice_date="2026-07-01",
            invoice_number="TA-2026-3098",
            invoice_total="531.00",
            purchase_order="PO-4010",
            subtotal="450.00",
            total_tax="81.00",
            vendor_name="Chennai Maintenance Pvt. Ltd.",
            vendor_gstin=vendors["chennai"],
            line_description="HVAC quarterly service",
            title="TAX INVOICE",
        ),
        SampleDoc(
            filename="11-mr-scan-quality.png",
            document_type="invoice",
            language="mr",
            layout="compact",
            pages=1,
            scenario="scan_quality",
            expected_issue_codes=[],
            currency="INR",
            customer_name=CUSTOMER_NAME,
            customer_gstin=customer,
            due_date="2026-07-31",
            invoice_date="2026-07-01",
            invoice_number="MR-2026-1111",
            invoice_total="88.50",
            purchase_order="PO-4011",
            subtotal="75.00",
            total_tax="13.50",
            vendor_name="Swachh Services Pvt. Ltd.",
            vendor_gstin=vendors["swachh"],
            line_description="Washroom consumables refill",
            title="TAX INVOICE",
        ),
        SampleDoc(
            filename="12-en-two-page.pdf",
            document_type="invoice",
            language="en",
            layout="modern",
            pages=2,
            scenario="happy_path",
            expected_issue_codes=[],
            currency="INR",
            customer_name=CUSTOMER_NAME,
            customer_gstin=customer,
            due_date="2026-07-31",
            invoice_date="2026-07-01",
            invoice_number="EN-2026-1212",
            invoice_total="708.00",
            purchase_order="PO-4012",
            subtotal="600.00",
            total_tax="108.00",
            vendor_name="Bharat Equipment Pvt. Ltd.",
            vendor_gstin=vendors["bharat"],
            line_description="Industrial vacuum equipment",
            title="TAX INVOICE",
        ),
        SampleDoc(
            filename="13-hi-fuel-receipt.png",
            document_type="receipt",
            language="hi",
            layout="compact",
            pages=1,
            scenario="fuel_receipt",
            expected_issue_codes=[],
            currency="INR",
            customer_name=None,
            customer_gstin=None,
            due_date=None,
            invoice_date="2026-07-19",
            invoice_number=None,
            invoice_total="59.00",
            purchase_order=None,
            subtotal="50.00",
            total_tax="9.00",
            vendor_name="Bharat Fuel Depot",
            vendor_gstin=vendors["fuel"],
            line_description="Diesel 4.2 L",
            title="FUEL RECEIPT / EENDHAN RECEIPT",
        ),
    ]


def _draw_invoice_pdf(path: Path, doc: SampleDoc) -> None:
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    y = height - 50

    def line(text: str, size: int = 11, gap: int = 16) -> None:
        nonlocal y
        c.setFont("Helvetica", size)
        c.drawString(50, y, text)
        y -= gap

    line(doc.title, size=16, gap=24)
    line(f"Vendor: {doc.vendor_name}")
    line(f"Vendor GSTIN: {doc.vendor_gstin or '—'}")
    line(f"Bill To: {doc.customer_name or '—'}")
    line(f"Customer GSTIN: {doc.customer_gstin or '—'}")
    line(CUSTOMER_ADDRESS)
    line(f"Invoice No: {doc.invoice_number or '—'}")
    line(f"Invoice Date: {doc.invoice_date}")
    line(f"Due Date: {doc.due_date or '—'}")
    line(f"Purchase Order: {doc.purchase_order or '—'}")
    line("")
    line(f"Description: {doc.line_description}")
    line(f"Subtotal: {doc.currency} {doc.subtotal}")
    line(f"GST (18%): {doc.currency} {doc.total_tax}")
    line(f"Total: {doc.currency} {doc.invoice_total}", size=12, gap=20)
    line(f"Language: {doc.language} | Layout: {doc.layout}")

    if doc.pages > 1:
        c.showPage()
        y = height - 50
        line("Page 2 — Line item detail", size=14, gap=22)
        line(f"1 x {doc.line_description}")
        line(f"Taxable value: {doc.currency} {doc.subtotal}")
        line(f"CGST/SGST or IGST: {doc.currency} {doc.total_tax}")
        line(f"Grand total: {doc.currency} {doc.invoice_total}")
        line("Thank you for your business.")

    c.save()


def _draw_image(path: Path, doc: SampleDoc, *, noisy: bool) -> None:
    width, height = (700, 900) if doc.document_type == "invoice" else (480, 720)
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    lines = [
        doc.title,
        "",
        f"Vendor: {doc.vendor_name}",
        f"Vendor GSTIN: {doc.vendor_gstin or '—'}",
    ]
    if doc.document_type == "invoice":
        lines.extend(
            [
                f"Bill To: {doc.customer_name}",
                f"Customer GSTIN: {doc.customer_gstin or '—'}",
                f"Invoice No: {doc.invoice_number}",
                f"Invoice Date: {doc.invoice_date}",
                f"Due Date: {doc.due_date}",
                f"PO: {doc.purchase_order or '—'}",
            ]
        )
    else:
        lines.extend(
            [
                f"Transaction Date: {doc.invoice_date}",
                "Expense Category: Fuel",
            ]
        )
    lines.extend(
        [
            "",
            f"Item: {doc.line_description}",
            f"Subtotal: {doc.currency} {doc.subtotal}",
            f"Tax: {doc.currency} {doc.total_tax}",
            f"Total: {doc.currency} {doc.invoice_total}",
        ]
    )
    y = 40
    for text in lines:
        draw.text((40, y), text, fill=(20, 20, 20), font=font)
        y += 22

    if noisy:
        pixels = image.load()
        assert pixels is not None
        for x in range(0, width, 3):
            for yy in range(0, height, 5):
                if (x + yy) % 7 == 0:
                    r, g, b = pixels[x, yy]
                    pixels[x, yy] = (min(255, r + 35), min(255, g + 30), min(255, b + 25))

    image.save(path, format="PNG")


def _manifest_entry(doc: SampleDoc) -> dict:
    return {
        "document_type": doc.document_type,
        "expected": {
            "currency": doc.currency,
            "customer_name": doc.customer_name,
            "customer_gstin": doc.customer_gstin,
            "document_type": doc.document_type,
            "due_date": doc.due_date,
            "invoice_date": doc.invoice_date,
            "invoice_number": doc.invoice_number,
            "invoice_total": doc.invoice_total,
            "purchase_order": doc.purchase_order,
            "subtotal": doc.subtotal,
            "total_tax": doc.total_tax,
            "vendor_name": doc.vendor_name,
            "vendor_gstin": doc.vendor_gstin,
        },
        "expected_issue_codes": doc.expected_issue_codes,
        "filename": doc.filename,
        "language": doc.language,
        "layout": doc.layout,
        "pages": doc.pages,
        "scenario": doc.scenario,
    }


def main() -> None:
    corpus = build_corpus()
    for doc in corpus:
        if doc.scenario != "total_mismatch":
            expected_total = _money(doc.subtotal) + _money(doc.total_tax)
            if expected_total != _money(doc.invoice_total):
                raise ValueError(
                    f"{doc.filename}: total {doc.invoice_total} != "
                    f"{doc.subtotal}+{doc.total_tax}"
                )
        else:
            if _money(doc.subtotal) + _money(doc.total_tax) == _money(doc.invoice_total):
                raise ValueError(f"{doc.filename}: expected a total mismatch")

    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    for old in GENERATED_DIR.iterdir():
        if old.is_file():
            old.unlink()

    for doc in corpus:
        path = GENERATED_DIR / doc.filename
        if path.suffix.lower() == ".pdf":
            _draw_invoice_pdf(path, doc)
        else:
            _draw_image(path, doc, noisy=doc.scenario in {"scan_quality", "fuel_receipt"})

    manifest = [_manifest_entry(doc) for doc in corpus]
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    pages = sum(doc.pages for doc in corpus)
    print(f"Wrote {len(corpus)} documents ({pages} pages) to {GENERATED_DIR}")
    print(f"Wrote manifest to {MANIFEST_PATH}")


if __name__ == "__main__":
    main()
