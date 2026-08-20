"""Playground: classify a sample invoice with the pipeline classifier."""

from __future__ import annotations

import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.config import get_settings  # noqa: E402
from app.pipeline.classification import DocumentClassifier, media_type_for_path  # noqa: E402

SAMPLE_INVOICE_PATH = (
    ROOT_DIR / "samples" / "generated" / "invoice-001234567-dia-zota.pdf"
)


def main() -> None:
    if not SAMPLE_INVOICE_PATH.exists():
        raise SystemExit(f"Sample not found: {SAMPLE_INVOICE_PATH}")
    settings = get_settings()
    if settings.openai_api_key.startswith("replace-with"):
        raise SystemExit("Set OPENAI_API_KEY in backend/.env before running this playground")

    classifier = DocumentClassifier(settings=settings)
    content_type = media_type_for_path(SAMPLE_INVOICE_PATH)
    classification = classifier.run(SAMPLE_INVOICE_PATH, content_type)
    print(json.dumps(classification.model_dump(mode="json"), indent=2))


if __name__ == "__main__":
    main()
