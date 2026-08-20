"""Orchestration for upload, pipeline, corrections, decisions, and drafts."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from app.accounting.catalog import list_gl_accounts
from app.accounting.selection import InvalidGLSelectionError, require_gl_account
from app.config import AppConfig, Settings, ensure_data_dirs
from app.correction_email.eligibility import is_correction_email_eligible
from app.document_review.provenance import apply_human_corrections
from app.document_review.review_fields import ReviewFields
from app.documents.models import (
    CorrectionEmailOut,
    DocumentDetail,
    DocumentSummary,
    GLAccountOut,
    IssueOut,
)
from app.documents.repository import (
    DocumentRepository,
    load_classification,
    load_fields,
    load_gl_suggestion,
    load_issues,
)
from app.documents.validation import has_blocking_errors, validate_document
from app.pipeline import build_default_pipeline
from app.pipeline.classification import DocumentClassifier
from app.providers.openai_correction_email import OpenAICorrectionEmailDrafter
from app.providers.openai_document_extractor import OpenAIDocumentExtractor
from app.providers.openai_gl_suggester import OpenAIGLSuggester


class DocumentServiceError(Exception):
    def __init__(self, message: str, *, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class DocumentService:
    def __init__(
        self,
        *,
        settings: Settings,
        config: AppConfig,
        repository: DocumentRepository,
        extractor: OpenAIDocumentExtractor | None = None,
        classifier: DocumentClassifier | None = None,
        gl_suggester: OpenAIGLSuggester | None = None,
        email_drafter: OpenAICorrectionEmailDrafter | None = None,
    ) -> None:
        self._settings = settings
        self._config = config
        self._repository = repository
        self._extractor = extractor or OpenAIDocumentExtractor(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
        )
        self._classifier = classifier or DocumentClassifier(settings=settings)
        self._gl_suggester = gl_suggester or OpenAIGLSuggester(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
        )
        self._email_drafter = email_drafter or OpenAICorrectionEmailDrafter(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
        )
        self._pipeline = build_default_pipeline(
            settings=settings,
            config=config,
            classifier=self._classifier,
            extractor=self._extractor,
            gl_suggester=self._gl_suggester,
            duplicate_checker=self._duplicate_checker,
        )
        ensure_data_dirs(config)

    def _duplicate_checker(self, fields: ReviewFields) -> bool:
        return self._repository.duplicate_exists(
            vendor_name=fields.vendor_name,
            invoice_number=fields.invoice_number,
        )

    def list_gl_accounts(self) -> list[GLAccountOut]:
        return [
            GLAccountOut(
                code=account.code.value,
                name=account.name,
                description=account.description,
            )
            for account in list_gl_accounts()
        ]

    def list_documents(self) -> list[DocumentSummary]:
        return [self._to_summary(row) for row in self._repository.list_documents()]

    def get_document(self, document_id: str) -> DocumentDetail:
        row = self._repository.get_document(document_id)
        if row is None:
            raise DocumentServiceError("Document not found", status_code=404)
        return self._to_detail(row)

    def get_stored_file(self, document_id: str) -> tuple[Path, str, str]:
        row = self._repository.get_document(document_id)
        if row is None:
            raise DocumentServiceError("Document not found", status_code=404)
        path = Path(row.stored_path)
        if not path.exists():
            raise DocumentServiceError("Stored file is missing", status_code=404)
        return path, row.content_type, row.filename

    def create_document(
        self,
        *,
        filename: str,
        content_type: str,
        payload: bytes,
    ) -> DocumentDetail:
        self._validate_upload(filename=filename, content_type=content_type, payload=payload)
        stored_path = self._store_upload(filename=filename, payload=payload)
        try:
            try:
                ctx = self._pipeline.run(stored_path, content_type=content_type)
            except Exception as exc:
                raise DocumentServiceError(
                    f"Document processing failed: {exc}",
                    status_code=502,
                ) from exc
            if ctx.review_data is None or ctx.issues is None or ctx.gl_suggestion is None:
                raise DocumentServiceError(
                    "Pipeline did not produce review data, issues, and GL suggestion",
                    status_code=502,
                )
            gl_code = ctx.gl_suggestion.account_code.value
            row = self._repository.create_document(
                filename=filename,
                content_type=content_type,
                stored_path=str(stored_path),
                fields=ctx.review_data,
                issues=ctx.issues,
                classification=ctx.classification,
                gl_suggestion=ctx.gl_suggestion,
                gl_account_code=gl_code,
            )
        except DocumentServiceError:
            if stored_path.exists():
                stored_path.unlink()
            raise
        except Exception:
            if stored_path.exists():
                stored_path.unlink()
            raise
        return self._to_detail(row)

    def update_fields(self, document_id: str, fields: ReviewFields) -> DocumentDetail:
        row = self._repository.get_document(document_id)
        if row is None:
            raise DocumentServiceError("Document not found", status_code=404)
        if row.status != "pending":
            raise DocumentServiceError("Only pending documents can be edited", status_code=409)

        current = load_fields(row)
        merged = apply_human_corrections(current, fields)
        duplicate = self._repository.duplicate_exists(
            vendor_name=merged.vendor_name,
            invoice_number=merged.invoice_number,
            exclude_id=document_id,
        )
        issues = validate_document(
            merged,
            duplicate_exists=duplicate,
            selected_gl_code=row.gl_account_code,
            config=self._config,
        )
        updated = self._repository.update_document(
            document_id,
            fields=merged,
            issues=issues,
        )
        if updated is None:
            raise DocumentServiceError("Document not found", status_code=404)
        return self._to_detail(updated)

    def update_accounting(self, document_id: str, gl_account_code: str) -> DocumentDetail:
        row = self._repository.get_document(document_id)
        if row is None:
            raise DocumentServiceError("Document not found", status_code=404)
        if row.status != "pending":
            raise DocumentServiceError("Only pending documents can be edited", status_code=409)
        try:
            account = require_gl_account(gl_account_code)
        except InvalidGLSelectionError as exc:
            raise DocumentServiceError(str(exc), status_code=422) from exc

        fields = load_fields(row)
        duplicate = self._repository.duplicate_exists(
            vendor_name=fields.vendor_name,
            invoice_number=fields.invoice_number,
            exclude_id=document_id,
        )
        issues = validate_document(
            fields,
            duplicate_exists=duplicate,
            selected_gl_code=account.code.value,
            config=self._config,
        )
        updated = self._repository.update_document(
            document_id,
            issues=issues,
            gl_account_code=account.code.value,
            update_gl_account=True,
        )
        if updated is None:
            raise DocumentServiceError("Document not found", status_code=404)
        return self._to_detail(updated)

    def decide(self, document_id: str, decision: str) -> DocumentDetail:
        row = self._repository.get_document(document_id)
        if row is None:
            raise DocumentServiceError("Document not found", status_code=404)
        if row.status != "pending":
            raise DocumentServiceError("Document already decided", status_code=409)

        fields = load_fields(row)
        if decision == "approve":
            status = "approved"
        elif decision == "reject":
            status = "rejected"
        else:
            raise DocumentServiceError("Decision must be approve or reject", status_code=422)

        duplicate = self._repository.duplicate_exists(
            vendor_name=fields.vendor_name,
            invoice_number=fields.invoice_number,
            exclude_id=document_id,
        )
        fresh_issues = validate_document(
            fields,
            duplicate_exists=duplicate,
            selected_gl_code=row.gl_account_code,
            config=self._config,
        )
        if decision == "approve":
            if has_blocking_errors(fresh_issues):
                raise DocumentServiceError(
                    "Cannot approve while error issues remain",
                    status_code=400,
                )
            if not row.gl_account_code:
                raise DocumentServiceError(
                    "A GL account is required for approval",
                    status_code=400,
                )
            try:
                require_gl_account(row.gl_account_code)
            except InvalidGLSelectionError as exc:
                raise DocumentServiceError(str(exc), status_code=422) from exc

        updated = self._repository.update_document(
            document_id,
            issues=fresh_issues,
            status=status,
            decided=True,
        )
        if updated is None:
            raise DocumentServiceError("Document not found", status_code=404)
        return self._to_detail(updated)

    def draft_correction_email(self, document_id: str) -> CorrectionEmailOut:
        row = self._repository.get_document(document_id)
        if row is None:
            raise DocumentServiceError("Document not found", status_code=404)
        issues = load_issues(row)
        if not is_correction_email_eligible(issues):
            raise DocumentServiceError(
                "Correction email is only available when supplier-fixable issues exist",
                status_code=400,
            )
        try:
            draft = self._email_drafter.draft(load_fields(row), issues)
        except Exception as exc:
            raise DocumentServiceError(
                f"Correction email drafting failed: {exc}",
                status_code=502,
            ) from exc
        return CorrectionEmailOut(subject=draft.subject, body=draft.body)

    def delete_document(self, document_id: str) -> None:
        row = self._repository.delete_document(document_id)
        if row is None:
            raise DocumentServiceError("Document not found", status_code=404)
        path = Path(row.stored_path)
        if path.exists():
            path.unlink()

    def _validate_upload(self, *, filename: str, content_type: str, payload: bytes) -> None:
        if not filename.strip():
            raise DocumentServiceError("Filename is required", status_code=422)
        if content_type not in self._config.allowed_content_types:
            raise DocumentServiceError(
                "Only PDF, PNG, and JPEG uploads are supported",
                status_code=422,
            )
        if len(payload) == 0:
            raise DocumentServiceError("Uploaded file is empty", status_code=422)
        if len(payload) > self._config.max_upload_bytes:
            raise DocumentServiceError("Upload exceeds the 4 MB limit", status_code=422)

    def _store_upload(self, *, filename: str, payload: bytes) -> Path:
        safe_name = Path(filename).name
        destination = self._config.uploads_dir / f"{uuid4()}-{safe_name}"
        destination.write_bytes(payload)
        return destination

    def _to_summary(self, row) -> DocumentSummary:
        fields = load_fields(row)
        return DocumentSummary(
            id=row.id,
            filename=row.filename,
            document_type=fields.document_type,
            status=row.status,
            vendor_name=row.vendor_name,
            invoice_number=row.invoice_number,
            total=None if fields.total is None else format(fields.total, "f"),
            currency=fields.currency,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def _to_detail(self, row) -> DocumentDetail:
        fields = load_fields(row)
        issues = load_issues(row)
        suggestion = load_gl_suggestion(row)
        return DocumentDetail(
            id=row.id,
            filename=row.filename,
            content_type=row.content_type,
            document_type=fields.document_type,
            status=row.status,
            fields=fields,
            issues=[IssueOut.from_issue(issue) for issue in issues],
            classification=load_classification(row),
            gl_suggestion=suggestion,
            gl_account_code=row.gl_account_code or None,
            correction_email_eligible=is_correction_email_eligible(issues),
            created_at=row.created_at,
            updated_at=row.updated_at,
            decided_at=row.decided_at,
        )
