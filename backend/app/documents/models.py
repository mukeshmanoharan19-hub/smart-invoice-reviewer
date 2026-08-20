"""SQLAlchemy DocumentRecord and API DTOs."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field
from sqlalchemy import DateTime, Index, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.document_review.review_fields import ReviewFields
from app.documents.validation import Issue
from app.pipeline.classification_models import DocumentClassification
from app.pipeline.gl_models import GlSuggestion


class Base(DeclarativeBase):
    pass


class DocumentRecord(Base):
    """One processed upload with per-stage JSON columns for inspection."""

    __tablename__ = "documents"
    __table_args__ = (
        Index("ix_documents_vendor_invoice", "vendor_name", "invoice_number"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(64), nullable=False)
    stored_path: Mapped[str] = mapped_column(Text, nullable=False)
    document_type: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    vendor_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    invoice_number: Mapped[str | None] = mapped_column(String(128), nullable=True)
    classification_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    review_data_json: Mapped[str] = mapped_column(Text, nullable=False)
    issues_json: Mapped[str] = mapped_column(Text, nullable=False)
    gl_suggestion_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    gl_account_code: Mapped[str | None] = mapped_column(String(16), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class IssueOut(BaseModel):
    code: str
    severity: Literal["error", "warning"]
    message: str
    field: str | None = None

    @classmethod
    def from_issue(cls, issue: Issue) -> IssueOut:
        return cls(
            code=issue.code,
            severity=issue.severity,
            message=issue.message,
            field=issue.field,
        )


class DocumentSummary(BaseModel):
    id: str
    filename: str
    document_type: Literal["invoice", "receipt"]
    status: Literal["pending", "approved", "rejected"]
    vendor_name: str | None
    invoice_number: str | None
    total: str | None
    currency: str | None
    created_at: datetime
    updated_at: datetime


class DocumentDetail(BaseModel):
    id: str
    filename: str
    content_type: str
    document_type: Literal["invoice", "receipt"]
    status: Literal["pending", "approved", "rejected"]
    fields: ReviewFields
    issues: list[IssueOut]
    classification: DocumentClassification | None = None
    gl_suggestion: GlSuggestion | None = None
    gl_account_code: str | None
    correction_email_eligible: bool = False
    created_at: datetime
    updated_at: datetime
    decided_at: datetime | None


class DocumentUpdateRequest(BaseModel):
    fields: ReviewFields


class AccountingUpdateRequest(BaseModel):
    gl_account_code: str = Field(min_length=1)


class DecisionRequest(BaseModel):
    decision: Literal["approve", "reject"]


class CorrectionEmailOut(BaseModel):
    subject: str
    body: str


class GLAccountOut(BaseModel):
    code: str
    name: str
    description: str


class HealthOut(BaseModel):
    status: Literal["ok"] = "ok"
