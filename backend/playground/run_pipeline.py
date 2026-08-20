"""Playground: run the full document-review pipeline on one sample."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.config import get_settings  # noqa: E402
from app.pipeline import build_default_pipeline, media_type_for_path  # noqa: E402

SAMPLE_PATH = ROOT_DIR / "samples" / "generated" / "invoice-001234567-dia-zota.pdf"


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    if not SAMPLE_PATH.exists():
        raise SystemExit(f"Sample not found: {SAMPLE_PATH}")
    settings = get_settings()
    if settings.openai_api_key.startswith("replace-with"):
        raise SystemExit("Set OPENAI_API_KEY in backend/.env before running this playground")

    pipeline = build_default_pipeline(settings=settings)
    ctx = pipeline.run(SAMPLE_PATH, content_type=media_type_for_path(SAMPLE_PATH))
    payload = {
        "classification": None
        if ctx.classification is None
        else ctx.classification.model_dump(mode="json"),
        "review_data": None if ctx.review_data is None else ctx.review_data.model_dump(mode="json"),
        "gl_suggestion": None
        if ctx.gl_suggestion is None
        else ctx.gl_suggestion.model_dump(mode="json"),
        "issues": None
        if ctx.issues is None
        else [
            {
                "code": issue.code,
                "severity": issue.severity,
                "message": issue.message,
                "field": issue.field,
            }
            for issue in ctx.issues
        ],
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
