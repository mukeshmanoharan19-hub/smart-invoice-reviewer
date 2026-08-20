# Build-along guide

This local guide records the OpenAI-only Invoice Review build for Northstar Facilities.

## Starter outcome

The repository installs reproducibly and starts a FastAPI service plus React interface for prepared invoice and receipt reviews.

## Why this boundary exists

Models extract evidence. Deterministic Python owns GSTIN checks, totals reconciliation, duplicate detection, and approval gates. Maya keeps the decision.

## Commands

```bash
cd backend
uv sync --locked

cd ../frontend
pnpm install --frozen-lockfile

cd ..
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# Set OPENAI_API_KEY and OPENAI_MODEL in backend/.env
```

Start the API:

```bash
cd backend
uv run --locked --no-sync uvicorn app.main:create_app --factory --reload --port 8000
```

Start the UI:

```bash
cd frontend
pnpm dev
```

## Important locations

- `docs/client-brief.md`: the recurring finance problem and definition of done
- `docs/architecture.md`: the intended boundaries and data flow
- `samples/generated/`: demo PDF invoices
- `backend/app/main.py`: FastAPI factory
- `backend/app/documents/`: routes, service, repository, validation
- `backend/app/providers/`: OpenAI adapters
- `frontend/src/App.tsx`: review workflow

## OpenAI-only extraction slice

### Outcome

Azure Document Intelligence was removed. A single OpenAI Responses API adapter classifies and extracts each upload. Deterministic normalization parses money and dates. FastAPI persists prepared reviews in SQLite. The React UI walks Maya from welcome through upload, processing, correction, GL override, decision, email draft, history, and deletion.

### Why

The product brief asks for a prepared review, not autonomous approval. One extractor keeps the teaching surface smaller while preserving the model-versus-policy split.

### Commands

```bash
cd backend
uv run --locked --no-sync ruff check app scripts
uv run --locked --no-sync python scripts/check_openai.py

cd ../frontend
pnpm exec tsc -b --pretty false
pnpm lint
pnpm build
```

### What you should observe

- `GET http://localhost:8000/health` returns `{"status":"ok"}`.
- `http://localhost:5173` shows the Invoice Review workflow.
- Uploading a sample PDF creates a review with extracted fields, policy issues, and a GL suggestion.
- Approval is blocked while error issues remain or no GL account is selected.
- Correction-email drafts can be copied; the app never sends them.

### Checkpoint

- [x] Azure Document Intelligence dependencies and adapters removed.
- [x] Backend lint passes for `app` and `scripts`.
- [x] Frontend type-check, lint, and production build pass.
- [ ] Live OpenAI probe prints a normalized review for one sample PDF after `OPENAI_API_KEY` is set.
- [ ] Manual browser walkthrough covers upload → review → decision → history → delete.

## Classification pipeline step

### Outcome

Uploads are classified as invoice or receipt before field extraction. `ClassificationStep` writes an immutable `PipelineContext` copy with `document_kind`, self-reported `confidence`, and `reasoning`. Extraction then runs for the classified kind only.

### Why

Classify first keeps the pipeline branchable and matches the teaching pattern from the [classification lesson](https://learn.datalumina.com/docs/invoice-review/classification). LLM confidence remains a rough signal; reasoning is often more useful for a reviewer.

### Commands

```bash
cd backend
uv run --locked --no-sync python -m playground.classify_sample_document
uv run --locked --no-sync ruff check app scripts playground
```

### What you should observe

- The playground prints JSON like `{"document_kind":"invoice","confidence":0.98,"reasoning":"..."}`.
- Review creation calls classification, then extraction, then policy and GL suggestion.

### Checkpoint

- [x] `DocumentClassifier` and `ClassificationStep` live under `app/pipeline/`.
- [x] OpenAI SDK usage for classification stays in `app/providers/openai_document_classifier.py`.
- [ ] Playground classifies a sample invoice after `OPENAI_API_KEY` is set.

## Chaining the pipeline

### Outcome

`Pipeline` in `app/pipeline/base.py` runs ordered steps against an immutable `PipelineContext`. Extraction, GL categorization, and validation are discrete steps. `build_default_pipeline` wires classify → extract → GL → validate.

### Why

A named chain makes steps swappable. Models extract evidence; validation stays pure Python with GSTIN checksum and totals checks.

### Commands

```bash
cd backend
uv run --locked --no-sync python -m playground.run_pipeline
uv run --locked --no-sync ruff check app scripts playground
```

### What you should observe

- Logs show numbered steps: classification, extraction, gl_categorization, validation.
- The payload includes classification reasoning, review fields, GL suggestion, and typed issues.

### Checkpoint

- [x] `Pipeline` / `PipelineStep` live in `app/pipeline/base.py`.
- [x] `ExtractionStep` and `ValidationStep` route and validate without Azure DI.
- [ ] `run_pipeline` playground completes after `OPENAI_API_KEY` is set.

## GL categorization

### Outcome

A separate GL step suggests one account from a fixed ten-code Northstar catalog. `account_code` is a `GlAccountCode` enum in structured output, so invented codes fail schema validation. The step reads normalized fields only, never the PDF bytes again.

### Why

One responsibility per step. The enum is the guardrail; the prompt is only guidance.

### Checkpoint

- [x] Catalog codes 6100–6190 live in `app/accounting/catalog.py`.
- [x] `GlCategorizationStep` is part of `build_default_pipeline`.
- [x] Review creation persists the suggested code and reasoning for Maya to override.

## API layer

### Outcome

The pipeline is reachable over HTTP. Resources are named `/api/documents` (not invoices) because receipts share the same flow. SQLite stores per-stage JSON plus indexed vendor/invoice columns. Accounting has its own router. Swagger at `/docs` can exercise the backend without the UI.

### Why

Endpoints are the doors to the backend. Proving them in Swagger before React keeps the boundaries visible: routes speak HTTP, the service runs the pipeline, the repository owns SQLite.

### Commands

```bash
cd backend
uv run --locked --no-sync uvicorn app.main:create_app --factory --reload --port 8000
```

Open `http://localhost:8000/docs` and try `POST /api/documents`.

### Checkpoint

- [x] `create_app` factory wires document and accounting routers.
- [x] Persistence uses `backend/data/documents.db` and stage JSON columns.
- [x] Frontend calls `/api/documents` and `/api/accounting/gl-accounts`.

## Frontend

### Outcome

The React app walks Maya through welcome → upload/preview → processing → review. Components match the tutorial names (`WelcomePortal`, `UploadStep`, `ProcessingStep`, `DocumentInbox`). Classification reasoning, extraction, validation issues, and GL suggestion are visible after process. `./scripts/dev.sh` starts both halves.

### Why

The frontend holds no business logic. Every click is an API call through `src/lib/api.ts`. See [api-and-pipeline.md](api-and-pipeline.md) for the button-to-route map.

### Commands

```bash
./scripts/dev.sh
# or
cd frontend && pnpm exec tsc -b --pretty false && pnpm lint && pnpm build
```

### Checkpoint

- [x] `./scripts/dev.sh` starts backend factory and Vite together.
- [x] `VITE_API_BASE_URL=/` is supported for same-origin builds.
- [x] Review screen shows classification, extraction, validation, and GL stages.

## Closing the loop

### Outcome

Maya can correct fields, approve/reject with error gating, and draft a supplier correction email only when supplier-fixable issues exist. Extracted fields carry `field_sources` (`openai` or `human`). Human edits clear per-field confidence and suppress the low-confidence warning.

### Why

Models extract evidence; Maya owns the decision. Provenance makes that split visible. Without Document Intelligence, hybrid merge is not used — OpenAI is the extractor, and provenance still tracks openai vs human.

### Checkpoint

- [x] `DocumentReviewStep` stamps openai sources after extraction.
- [x] `apply_human_corrections` marks edits as human and revalidates.
- [x] `correction_email/eligibility.py` gates the draft endpoint and UI button.
- [x] Manifest/corpus evaluator remains out of scope for this OpenAI-only build.
