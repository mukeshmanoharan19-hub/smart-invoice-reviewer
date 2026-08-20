"""OpenAI GL account suggestion from normalized review fields only."""

from __future__ import annotations

from openai import OpenAI
from pydantic import BaseModel, Field

from app.accounting.catalog import GlAccountCode, catalog_prompt_lines
from app.accounting.selection import require_gl_account
from app.document_review.review_fields import ReviewFields
from app.pipeline.gl_models import GlSuggestion


class GLSuggestionWire(BaseModel):
    account_code: GlAccountCode
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str = Field(min_length=1)


class OpenAIGLSuggester:
    """Provider adapter: OpenAI SDK types stop in this module.

    Reads normalized fields only — never the original document bytes.
    """

    def __init__(self, api_key: str, model: str) -> None:
        self._client = OpenAI(api_key=api_key)
        self._model = model

    def suggest(self, fields: ReviewFields) -> GlSuggestion:
        payload = fields.model_dump(mode="json")
        response = self._client.responses.parse(
            model=self._model,
            input=[
                {
                    "role": "user",
                    "content": (
                        "Suggest exactly one Northstar GL account for this document.\n"
                        f"Catalog:\n{catalog_prompt_lines()}\n\n"
                        f"Normalized fields JSON:\n{payload}\n\n"
                        "Choose only a catalog code. "
                        "confidence is a rough self-reported signal. Explain briefly."
                    ),
                }
            ],
            text_format=GLSuggestionWire,
        )
        parsed = response.output_parsed
        if parsed is None:
            raise RuntimeError("OpenAI returned no GL suggestion payload")
        account = require_gl_account(parsed.account_code.value)
        return GlSuggestion(
            account_code=account.code,
            confidence=parsed.confidence,
            reasoning=parsed.reasoning.strip(),
        )
