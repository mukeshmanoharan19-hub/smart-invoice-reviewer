"""OpenAI Responses API adapter for document kind classification."""

from __future__ import annotations

import base64
from pathlib import Path

from openai import OpenAI

from app.pipeline.classification_models import DocumentClassification

CLASSIFICATION_INSTRUCTIONS = """
You classify Indian supplier financial documents for Northstar Facilities.

Choose exactly one document_kind:
- invoice: a bill from a supplier requesting payment (invoice number, customer details,
  GSTIN, payment terms / due date are typical signals)
- receipt: proof of an already-paid expense (merchant, transaction date, paid total)

confidence is a self-reported float from 0.0 to 1.0. It is a rough signal, not a
calibrated probability.
reasoning should briefly cite the visual or textual cues that drove the decision.
""".strip()

CLASSIFICATION_PROMPT = (
    "Classify this document as invoice or receipt. Return structured output only."
)


class OpenAIDocumentClassifier:
    """Provider adapter: OpenAI SDK types stop in this module."""

    def __init__(self, api_key: str, model: str) -> None:
        self._client = OpenAI(api_key=api_key)
        self._model = model

    def classify(self, path: Path, content_type: str) -> DocumentClassification:
        file_bytes = path.read_bytes()
        encoded = base64.b64encode(file_bytes).decode("ascii")
        content: list[dict[str, str]] = [
            {
                "type": "input_text",
                "text": f"{CLASSIFICATION_INSTRUCTIONS}\n\n{CLASSIFICATION_PROMPT}",
            },
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
            text_format=DocumentClassification,
        )
        parsed = response.output_parsed
        if parsed is None:
            raise RuntimeError("OpenAI returned no structured classification payload")
        return parsed
