# API and pipeline map

A short wiring guide so button clicks stay traceable from React to FastAPI to pipeline steps.

## Run both halves

```bash
./scripts/dev.sh
```

- Backend: `http://localhost:8000` (Swagger at `/docs`)
- Frontend: `http://localhost:5173`
- Ctrl+C stops both processes

## Frontend → API

| UI action | Client | HTTP |
| --- | --- | --- |
| Process upload | `api.createReview` | `POST /api/documents` |
| Open inbox item | `api.getReview` | `GET /api/documents/{id}` |
| Save field corrections | `api.updateReview` | `PUT /api/documents/{id}` |
| Override GL account | `api.updateAccounting` | `PUT /api/documents/{id}/accounting` |
| Approve / reject | `api.decide` | `POST /api/documents/{id}/decision` |
| Draft correction email | `api.draftCorrectionEmail` | `POST /api/documents/{id}/correction-email` |
| Delete history item | `api.deleteReview` | `DELETE /api/documents/{id}` |
| Load GL catalog | `api.listGlAccounts` | `GET /api/accounting/gl-accounts` |

`VITE_API_BASE_URL` is `http://localhost:8000` in local `.env`. Set it to `/` for same-origin deployments so fetches stay relative.

## Pipeline chain

`POST /api/documents` stores the upload, then runs:

1. `classification`
2. `extraction`
3. `document_review` (stamps `openai` field sources)
4. `gl_categorization`
5. `validation`

Field edits via `PUT /api/documents/{id}` mark changed fields as `human`, clear their model confidence, and re-run policy. Correction emails draft only when supplier-fixable issue codes are present.
