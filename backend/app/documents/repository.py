"""SQLite persistence for processed documents."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import and_, select
from sqlalchemy.orm import sessionmaker

from app.document_review.review_fields import ReviewFields
from app.documents.models import Base, DocumentRecord
from app.documents.validation import Issue
from app.pipeline.classification_models import DocumentClassification
from app.pipeline.gl_models import GlSuggestion


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class DocumentRepository:
    def __init__(self, session_factory: sessionmaker) -> None:
        self._session_factory = session_factory

    def create_document(
        self,
        *,
        filename: str,
        content_type: str,
        stored_path: str,
        fields: ReviewFields,
        issues: list[Issue],
        classification: DocumentClassification | None,
        gl_suggestion: GlSuggestion | None,
        gl_account_code: str | None,
    ) -> DocumentRecord:
        now = _utcnow()
        row = DocumentRecord(
            id=str(uuid4()),
            filename=filename,
            content_type=content_type,
            stored_path=stored_path,
            document_type=fields.document_type,
            status="pending",
            vendor_name=fields.vendor_name,
            invoice_number=fields.invoice_number,
            classification_json=None
            if classification is None
            else classification.model_dump_json(),
            review_data_json=fields.model_dump_json(),
            issues_json=_issues_to_json(issues),
            gl_suggestion_json=None if gl_suggestion is None else gl_suggestion.model_dump_json(),
            gl_account_code=gl_account_code,
            created_at=now,
            updated_at=now,
            decided_at=None,
        )
        with self._session_factory() as session:
            session.add(row)
            session.commit()
            session.refresh(row)
            return row

    def list_documents(self) -> list[DocumentRecord]:
        with self._session_factory() as session:
            statement = select(DocumentRecord).order_by(DocumentRecord.created_at.desc())
            return list(session.scalars(statement))

    def get_document(self, document_id: str) -> DocumentRecord | None:
        with self._session_factory() as session:
            return session.get(DocumentRecord, document_id)

    def update_document(
        self,
        document_id: str,
        *,
        fields: ReviewFields | None = None,
        issues: list[Issue] | None = None,
        gl_account_code: str | None = None,
        update_gl_account: bool = False,
        status: str | None = None,
        decided: bool = False,
    ) -> DocumentRecord | None:
        with self._session_factory() as session:
            row = session.get(DocumentRecord, document_id)
            if row is None:
                return None
            if fields is not None:
                row.review_data_json = fields.model_dump_json()
                row.document_type = fields.document_type
                row.vendor_name = fields.vendor_name
                row.invoice_number = fields.invoice_number
            if issues is not None:
                row.issues_json = _issues_to_json(issues)
            if update_gl_account:
                row.gl_account_code = gl_account_code
            if status is not None:
                row.status = status
            if decided:
                row.decided_at = _utcnow()
            row.updated_at = _utcnow()
            session.commit()
            session.refresh(row)
            return row

    def delete_document(self, document_id: str) -> DocumentRecord | None:
        with self._session_factory() as session:
            row = session.get(DocumentRecord, document_id)
            if row is None:
                return None
            session.delete(row)
            session.commit()
            return row

    def duplicate_exists(
        self,
        *,
        vendor_name: str | None,
        invoice_number: str | None,
        exclude_id: str | None = None,
    ) -> bool:
        if not vendor_name or not invoice_number:
            return False
        with self._session_factory() as session:
            statement = select(DocumentRecord).where(
                and_(
                    DocumentRecord.document_type == "invoice",
                    DocumentRecord.vendor_name == vendor_name,
                    DocumentRecord.invoice_number == invoice_number,
                )
            )
            for row in session.scalars(statement):
                if exclude_id and row.id == exclude_id:
                    continue
                return True
        return False


def load_fields(row: DocumentRecord) -> ReviewFields:
    return ReviewFields.model_validate_json(row.review_data_json)


def load_issues(row: DocumentRecord) -> list[Issue]:
    payload = json.loads(row.issues_json)
    return [
        Issue(
            code=item["code"],
            severity=item["severity"],
            message=item["message"],
            field=item.get("field"),
        )
        for item in payload
    ]


def load_classification(row: DocumentRecord) -> DocumentClassification | None:
    if not row.classification_json:
        return None
    return DocumentClassification.model_validate_json(row.classification_json)


def load_gl_suggestion(row: DocumentRecord) -> GlSuggestion | None:
    if not row.gl_suggestion_json:
        return None
    return GlSuggestion.model_validate_json(row.gl_suggestion_json)


def _issues_to_json(issues: list[Issue]) -> str:
    return json.dumps(
        [
            {
                "code": issue.code,
                "severity": issue.severity,
                "message": issue.message,
                "field": issue.field,
            }
            for issue in issues
        ]
    )


def init_database(engine) -> None:
    Base.metadata.create_all(engine)
