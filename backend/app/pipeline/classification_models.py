"""Provider-independent classification result models."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class DocumentKind(StrEnum):
    invoice = "invoice"
    receipt = "receipt"


class DocumentClassification(BaseModel):
    document_kind: DocumentKind
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
