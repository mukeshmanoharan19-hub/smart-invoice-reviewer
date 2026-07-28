# Build-along guide

The complete guided build lives at <https://learn.datalumina.com/docs/invoice-review>. This local guide records the starter checkpoint plus the India/GSTIN localization of the brief and sample corpus.

## Starter outcome

The repository installs reproducibly, starts a minimal FastAPI service and React interface, and includes an India-localized business brief plus a fictional GSTIN sample corpus.

## Why this boundary exists

The starter removes the completed workflow while preserving every prerequisite needed to build it. You begin with the user, the source documents, and explicit service boundaries instead of reverse-engineering a finished application. The company, tax IDs, currency, and languages are Indian so policy work targets GSTIN and INR from the first slice.

## Commands

```bash
cd backend
uv sync --locked

cd ../frontend
pnpm install --frozen-lockfile

cd ..
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
./scripts/dev.sh --check
./scripts/dev.sh
```

## Important locations

- `docs/client-brief.md`: the recurring finance problem and definition of done
- `docs/architecture.md`: the intended boundaries and data flow
- `samples/`: the fictional evaluation corpus and manifest
- `backend/app/main.py`: the initial API boundary
- `frontend/src/App.tsx`: the initial interface boundary

## What you should observe

- `GET http://localhost:8000/health` returns `{"status":"ok"}`.
- `http://localhost:5173` shows the Invoice Review starter screen.
- `samples/manifest.json` lists 13 documents with INR amounts and GSTIN fields.
- No Azure request occurs at this checkpoint.

## Checkpoint

- [ ] Locked backend and frontend installs succeed.
- [ ] Backend lint passes.
- [ ] Frontend type-check, lint, and production build pass.
- [ ] `./scripts/dev.sh --check` reports that Invoice Review is ready to start.
- [ ] The health endpoint and starter screen load locally.

Continue with the [online tutorial](https://learn.datalumina.com/docs/invoice-review).

## Document Intelligence invoice probe

### Outcome

`DocumentIntelligenceService` is a small extraction class for `prebuilt-invoice` and `prebuilt-receipt`. Playground scripts load local credentials, run Document Intelligence, map fields into Pydantic schemas under `app/schemas/`, and print the filled models.

### Why

Before wiring FastAPI routes or policy rules, confirm Azure extraction and that invoice/receipt fields can be mapped into provider-independent Pydantic models. Keep runnable examples in `playground/`.

### Commands

```bash
cd backend
uv run --locked --no-sync python -m playground.analyze_sample_invoice
uv run --locked --no-sync python -m playground.analyze_sample_receipt
```

### What you should observe

- Schemas live under `app/schemas/invoice` and `app/schemas/receipt`, with shared money/address/confidence types in `app/schemas/common.py`.
- The invoice playground analyzes `samples/generated/invoice-001234567-dia-zota.pdf` and prints a mapped `Invoice` JSON model.
- The receipt playground analyzes Microsoft’s public Contoso sample receipt URL with `prebuilt-receipt` and prints a mapped `Receipt` JSON model.
- Mapped fields include identities, dates, money amounts with currency, line items, and optional tax details.

### Checkpoint

- [ ] Document Intelligence credentials are set in `backend/.env`.
- [ ] Invoice and receipt playgrounds print filled Pydantic models.
- [ ] Backend lint passes for `app` and `playground`.
