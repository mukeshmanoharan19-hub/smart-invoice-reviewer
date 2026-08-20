"""Provider-independent GL suggestion model used by the pipeline context."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.accounting.catalog import GlAccountCode


class GlSuggestion(BaseModel):
    account_code: GlAccountCode
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str = Field(min_length=1)
