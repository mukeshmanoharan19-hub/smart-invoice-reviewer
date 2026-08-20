"""OpenAI correction-email draft from review fields and policy issues."""

from __future__ import annotations

from openai import OpenAI
from pydantic import BaseModel, Field

from app.document_review.review_fields import ReviewFields
from app.documents.validation import Issue


class CorrectionEmailWire(BaseModel):
    subject: str = Field(min_length=1)
    body: str = Field(min_length=1)


class CorrectionEmailDraft:
    def __init__(self, subject: str, body: str) -> None:
        self.subject = subject
        self.body = body


class OpenAICorrectionEmailDrafter:
    def __init__(self, api_key: str, model: str) -> None:
        self._client = OpenAI(api_key=api_key)
        self._model = model

    def draft(self, fields: ReviewFields, issues: list[Issue]) -> CorrectionEmailDraft:
        issue_lines = "\n".join(
            f"- [{issue.severity}] {issue.code}: {issue.message}" for issue in issues
        ) or "- (no issues listed)"
        response = self._client.responses.parse(
            model=self._model,
            input=[
                {
                    "role": "user",
                    "content": (
                        "Draft a polite supplier correction email for Northstar Facilities "
                        "Pvt. Ltd. Do not claim the email was sent. Ask only for corrections "
                        "needed to fix the listed issues.\n\n"
                        f"Fields JSON:\n{fields.model_dump(mode='json')}\n\n"
                        f"Issues:\n{issue_lines}"
                    ),
                }
            ],
            text_format=CorrectionEmailWire,
        )
        parsed = response.output_parsed
        if parsed is None:
            raise RuntimeError("OpenAI returned no correction-email payload")
        return CorrectionEmailDraft(subject=parsed.subject.strip(), body=parsed.body.strip())
