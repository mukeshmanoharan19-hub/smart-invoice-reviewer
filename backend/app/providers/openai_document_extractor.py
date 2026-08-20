"""OpenAI Responses API adapter for document field extraction."""

from __future__ import annotations

import base64
from pathlib import Path

from openai import OpenAI

from app.document_review.extraction_models import DocumentExtractionWire
from app.document_review.normalize import normalize_extraction
from app.document_review.review_fields import ReviewFields
from app.pipeline.classification_models import DocumentKind

EXTRACTION_INSTRUCTIONS = """
You extract structured fields from an Indian supplier financial document.

The document kind is already classified. Extract only the fields that appear.
- For invoices: vendor, customer, GSTINs, invoice number/date, due date, PO, totals, lines.
- For receipts: merchant, transaction date, tax, total, and line items when present.

Return GSTIN values in the tax id fields when present.
Return every date as YYYY-MM-DD.
Return every money amount as a plain decimal string without currency symbols.
Set currency_code to INR when the document uses Indian rupees.
Confidence scores are self-reported floats from 0.0 to 1.0.
If a field is absent, leave it null. Do not invent values.
""".strip()


class OpenAIDocumentExtractor:
    """Provider adapter: OpenAI SDK types stop in this module."""

    def __init__(self, api_key: str, model: str) -> None:
        self._client = OpenAI(api_key=api_key)
        self._model = model

    def extract(
        self,
        path: Path,
        content_type: str,
        *,
        document_kind: DocumentKind,
        classification_confidence: float | None = None,
    ) -> ReviewFields:
        wire = self._parse_document(path, content_type, document_kind=document_kind)
        return normalize_extraction(
            wire,
            document_type=document_kind.value,
            classification_confidence=classification_confidence,
        )

    def _parse_document(
        self,
        path: Path,
        content_type: str,
        *,
        document_kind: DocumentKind,
    ) -> DocumentExtractionWire:
        file_bytes = path.read_bytes()
        encoded = base64.b64encode(file_bytes).decode("ascii")
        prompt = (
            f"{EXTRACTION_INSTRUCTIONS}\n\n"
            f"This document was classified as: {document_kind.value}."
        )
        content: list[dict[str, str]] = [
            {"type": "input_text", "text": prompt},
        ]
        if content_type == "application/pdf":
            content.append(
                {
                    "type": "input_file",
                    "filename": path.name,
                    "file_data": f"data:application/pdf;base64,{encoded}",
                }
            )
        else:
            mime = "image/jpeg" if content_type in {"image/jpeg", "image/jpg"} else content_type
            content.append(
                {
                    "type": "input_image",
                    "image_url": f"data:{mime};base64,{encoded}",
                }
            )

        response = self._client.responses.parse(
            model=self._model,
            input=[{"role": "user", "content": content}],
            text_format=DocumentExtractionWire,
        )
        parsed = response.output_parsed
        if parsed is None:
            raise RuntimeError("OpenAI returned no structured extraction payload")
        return parsed
