# Invoice Review

Local full-stack invoice and receipt review for Northstar Facilities Pvt. Ltd. OpenAI extracts document fields. Deterministic Python validates GSTIN and policy. A React UI prepares the review for a human decision.

## What is included

- Client brief and target architecture
- Sample PDF invoices under `samples/generated/`
- FastAPI backend with OpenAI extraction, GL suggestion, correction-email drafting, SQLite history
- React review interface
- Exact dependency pins and lockfiles

## Prerequisites

- Python 3.12 or newer
- uv
- Node.js 22 or newer
- pnpm 11 (optional on PATH; Make/`scripts/dev.sh` fall back to `npx pnpm@11.3.0`)

## Install and run (Makefile)

```bash
make install   # uv sync + pnpm install (locked)
make env       # copy .env.example → .env if missing
# edit backend/.env: OPENAI_API_KEY=...  (OPENAI_MODEL=gpt-4.1)
make dev       # API :8000 + Vite UI
```

- UI: Vite prints the local URL (usually `http://localhost:5173`)
- API docs: `http://localhost:8000/docs`
- `make help` lists all targets (`backend`, `frontend`, `verify`, …)

Manual equivalents (without Make) are still valid: `uv sync --locked`, `pnpm install --frozen-lockfile`, `./scripts/dev.sh`.

Start with [the client brief](docs/client-brief.md) and [architecture](docs/architecture.md).
