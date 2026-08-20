# Backend agent instructions

Read [../AGENTS.md](../AGENTS.md) first. The root file contains the project-wide product boundaries, dependency policy, teaching rules, and verification policy. This file adds backend-specific conventions.

## Stack

- Python 3.12 or newer.
- `uv` for dependency and project management.
- FastAPI and uvicorn for the HTTP service.
- Pydantic v2 and pydantic-settings for typed boundaries and provider settings.
- SQLAlchemy 2 with local SQLite persistence.
- OpenAI Responses API behind provider adapters.
- Ruff for linting and import/style checks.

The stack is locked unless Dave explicitly approves a change.

## Layout

```text
backend/
├── app/
│   ├── main.py              # FastAPI construction and dependency wiring
│   ├── config.py            # Provider settings and fixed application config
│   ├── documents/           # HTTP, orchestration, persistence, and policy
│   ├── accounting/          # Fixed GL catalog, selection, and accounting routes
│   ├── document_review/     # Wire models, normalization, and review fields
│   ├── pipeline/            # Pipeline runner, classify/extract/GL/validate steps
│   └── providers/           # OpenAI SDK adapters; SDK types stop here
├── playground/              # Interactive provider and pipeline probes
├── scripts/                 # Explicit provider checks
├── pyproject.toml
└── uv.lock
```

## Boundaries and code style

- Routes own HTTP parsing, response models, and status-code translation.
- Services orchestrate the user workflow and depend on explicit interfaces.
- Repositories own SQLAlchemy and SQLite access.
- Provider adapters are the only modules allowed to expose third-party SDK types.
- Deterministic validation and reconciliation remain separate from AI extraction or generation.
- Keep public functions typed and modules focused. Prefer dataclasses, enums, `pathlib`, and other standard-library capabilities over helper packages.
- Validate files, HTTP input, provider output, and database writes at their boundaries. Do not repeatedly validate trusted internal calls.
- The current OpenAI and SQLite clients are synchronous. Use normal FastAPI `def` handlers for synchronous request paths instead of blocking an async event loop.
- Do not add auth, queues, workers, caching, analytics, deployment code, or accounting integrations unless the user story changes.

## Configuration

- `app/config.py` is the only backend configuration boundary.
- Provider credentials and model names are read through its Pydantic `Settings` model.
- Fixed tutorial policy belongs in its immutable application configuration, not environment variables.
- Never call `os.getenv`, read `os.environ`, or call `load_dotenv` in application modules or scripts.
- Fail clearly when required provider configuration is absent. Do not hide configuration failures behind silent fallbacks.
- Never commit `.env`, OpenAI keys, uploaded documents, SQLite databases, or generated runtime data.

## Dependencies

- Never add a dependency without Dave's explicit approval.
- Use exact direct versions and commit `uv.lock` with every approved dependency change.
- Keep `add-bounds = "exact"` and `exclude-newer = "7 days"` under `[tool.uv]`.
- Install with `uv sync --locked`.
- Commands that must use the existing environment run through `uv run --locked --no-sync`.
- Prefer a small local function when a dependency would only replace a few clear standard-library lines.

## Verification

```bash
uv sync --locked
uv run --locked --no-sync ruff check app scripts
uv run --locked --no-sync python scripts/check_openai.py
```

Provider checks may consume paid OpenAI capacity. Document expected calls before running them. Complete verification also includes startup readiness and the manual end-to-end workflow.

Do not add `tests/`, `pytest`, or committed automated test files.
