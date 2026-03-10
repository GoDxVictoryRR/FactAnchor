# Canonical File Tree

```
factanchor/
├── .github/
│   └── workflows/
│       ├── ci.yml                    # Lint, test, build on every PR
│       └── deploy.yml                # Deploy to staging on merge to main
├── docker/
│   ├── api.Dockerfile
│   ├── worker.Dockerfile
│   └── frontend.Dockerfile
├── docker-compose.yml                # Full local stack
├── docker-compose.test.yml           # Test isolation stack
├── .env.example                      # All required env vars, no real values
│
├── backend/
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   │       └── 0001_initial_schema.py
│   │
│   ├── app/
│   │   ├── main.py                   # FastAPI app factory
│   │   ├── config.py                 # Pydantic Settings (reads .env)
│   │   ├── dependencies.py           # FastAPI dependency injection
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── router.py             # Top-level API router
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── reports.py        # POST /reports, GET /reports/{id}
│   │   │   │   ├── claims.py         # GET /reports/{id}/claims
│   │   │   │   └── health.py         # GET /health, GET /ready
│   │   │   └── ws/
│   │   │       └── verification.py   # WS /ws/reports/{id}/stream
│   │   │
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── jwt.py                # JWT encode/decode, token refresh
│   │   │   ├── middleware.py         # Auth middleware, rate limiting
│   │   │   └── models.py             # User, ApiKey models
│   │   │
│   │   ├── nlp/
│   │   │   ├── __init__.py
│   │   │   ├── extractor.py          # Main claim extraction pipeline
│   │   │   ├── classifiers.py        # SQL vs Vector routing logic
│   │   │   ├── models.py             # Claim, Entity dataclasses
│   │   │   └── pipeline.py           # spaCy pipeline loader + caching
│   │   │
│   │   ├── verification/
│   │   │   ├── __init__.py
│   │   │   ├── sql_verifier.py       # LLM → SQL → execute → reconcile
│   │   │   ├── vector_verifier.py    # Embed claim → Pinecone query → score
│   │   │   ├── reconciler.py         # Merge results → VERIFIED/FLAGGED/UNCERTAIN
│   │   │   └── confidence.py         # SHA-256 Confidence Score generation
│   │   │
│   │   ├── workers/
│   │   │   ├── __init__.py
│   │   │   ├── celery_app.py         # Celery app factory + config
│   │   │   ├── tasks.py              # verify_claim task, report_complete task
│   │   │   └── signals.py            # Task success/failure signal handlers
│   │   │
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── session.py            # SQLAlchemy engine + session factory
│   │   │   ├── models.py             # Report, Claim, VerificationResult ORM models
│   │   │   └── repositories.py       # Data access layer (no raw SQL in services)
│   │   │
│   │   └── schemas/
│   │       ├── __init__.py
│   │       ├── report.py             # Pydantic request/response schemas
│   │       ├── claim.py
│   │       └── verification.py
│   │
│   └── tests/
│       ├── conftest.py               # Pytest fixtures, test DB, mock Celery
│       ├── unit/
│       │   ├── test_extractor.py
│       │   ├── test_sql_verifier.py
│       │   ├── test_vector_verifier.py
│       │   ├── test_confidence.py
│       │   └── test_classifiers.py
│       └── integration/
│           ├── test_reports_api.py
│           ├── test_websocket.py
│           └── test_worker_pipeline.py
│
├── frontend/
│   ├── package.json
│   ├── svelte.config.js
│   ├── vite.config.ts
│   ├── src/
│   │   ├── app.html
│   │   ├── app.css
│   │   ├── lib/
│   │   │   ├── api/
│   │   │   │   ├── client.ts         # Typed API client (fetch wrapper)
│   │   │   │   └── websocket.ts      # WS connection + reconnect logic
│   │   │   ├── stores/
│   │   │   │   ├── report.ts         # Active report state
│   │   │   │   └── auth.ts           # Auth token store
│   │   │   └── components/
│   │   │       ├── ReportViewer.svelte   # Highlighted document display
│   │   │       ├── ClaimBadge.svelte     # Per-claim status badge
│   │   │       ├── ConfidenceScore.svelte # Score + hash display
│   │   │       ├── UploadPanel.svelte     # Report input
│   │   │       └── VerificationStream.svelte # Live WS progress
│   │   └── routes/
│   │       ├── +layout.svelte
│   │       ├── +page.svelte          # Home / upload
│   │       └── report/
│   │           └── [id]/
│   │               └── +page.svelte  # Report verification view
│   └── tests/
│       └── components/
│           ├── ReportViewer.test.ts
│           └── ConfidenceScore.test.ts
│
└── infra/
    ├── nginx/
    │   └── nginx.conf                # Reverse proxy, WS upgrade headers
    └── pgbouncer/
        └── pgbouncer.ini             # Connection pool config
```
