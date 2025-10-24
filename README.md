# GetEmpStatus Service

A single-endpoint FastAPI service that returns an employee’s pay metrics and status based on business rules, with optional caching, DB logging, retries, and bearer-token protection.

## Table of Contents
- [Overview](#overview)
- [API](#api)
- [Business Rules](#business-rules)
- [Errors](#errors)
- [Environment & Configuration](#environment--configuration)
- [Run Locally](#run-locally)
- [Testing](#testing)
- [Postman Collection](#postman-collection)
- [Architecture](#architecture)
- [Data Model & Seed](#data-model--seed)
- [Caching, Logging, Retries](#caching-logging-retries)
- [Troubleshooting](#troubleshooting)

## Overview
- Framework: FastAPI + SQLAlchemy
- DB: SQLite by default (switch with `DATABASE_URL`)
- Endpoint: `POST /api/GetEmpStatus`
- Bonus: TTL cache, DB logger, DB retries, optional bearer token

## API
### Request
```http
POST /api/GetEmpStatus
Content-Type: application/json
Authorization: Bearer <token>        # optional; required only if API_TOKEN is set
```
Body:
```json
{ "NationalNumber": "NAT1001" }
```

### Successful Response (200)
```json
{
  "user": {
   "username": "john",
    "nationalNumber": "NAT1001",
    "email": "john@example.com",
    "phone": "555-0100",
    "isActive": true
  },
  "metrics": {
    "count": 12,
    "sum": 12345.67,
    "sumAfterTax": 11481.47,
    "average": 956.79,
    "highest": 2200.00
  },
  "status": "GREEN",
  "lastUpdatedUtc": "2025-10-24T18:12:04Z"
}
```

## Business Rules
- Monthly adjustments:
  - **December**: +10%
  - **June–August**: –5%
- Tax: If adjusted **total > 10,000**, apply **7%** deduction to the total. `average` uses the post-tax total.
- Status by average:
  - `> 2000` → **GREEN**
  - `= 2000` → **ORANGE**
  - `< 2000` → **RED**
- Requires **at least 3** salary rows for active users.

## Errors
All business/HTTP errors are returned as:
```json
{ "error": "<message>" }
```

Typical cases:
- `404` — `{ "error": "Invalid National Number" }`
- `406` — `{ "error": "User is not Active" }`
- `422` — `{ "error": "INSUFFICIENT_DATA" }` (active user with <3 salary rows)
- `401` — `{ "error": "Unauthorized" }` (when `API_TOKEN` is set and header is missing/invalid)

Validation errors (malformed payload) return:
```json
{
  "error": "VALIDATION_ERROR",
  "details": [ ... FastAPI validation errors ... ]
}
```

## Environment & Configuration
| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./local.db` | DB connection string |
| `API_TOKEN` | *(unset)* | If set, enables bearer auth. |
| `CACHE_TTL_SECONDS` | `60` | Cache TTL seconds for employee responses |
| `LOG_TO_DB` | `1` | `1` to enable DB logging to `logs` table |

## Run Locally
```bash
python -m venv .venv
source .venv/bin/activate           # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open Swagger UI at `http://localhost:8000/docs`.

## Testing
```bash
pytest -vv --log-cli-level=INFO
```

## Postman Collection
Import `postman/GetEmpStatus.postman_collection.json`. The `Authorization` header is **disabled by default**; enable and set `{API_TOKEN}}` only if you configured one.

## Architecture
- `app/main.py` — FastAPI app, lifespan bootstrap, **error envelope mappers**.
- `app/api.py` — `/api/GetEmpStatus` route, cache usage, response mapping.
- `app/process_status.py` — Core business logic (monthly adjustments, tax, metrics, status).
- `app/data_access.py` — SQLAlchemy engine/session and **retrying** DAO.
- `app/models.py` — ORM models (`users`, `salaries`, `logs`).
- `app/logger.py` — Thin DB logger (optional).
- `app/cache.py` — In-memory TTL cache (**now thread-safe**).
- `app/settings.py` — Config via env vars.
- `app/bootstrap.py` — Schema + **seed** loader.
- `app/schema.py` — Pydantic request/response models.

## Data Model & Seed
See `db/seed.sql` for sample users/salaries. The app loads it at startup (idempotent).

## Caching, Logging, Retries
- Caching: key = `empstatus:<nationalNumber>`, TTL=`CACHE_TTL_SECONDS`. Bypass by adding `?bustCache=true` to the request URL.
- Logging: each call writes decision context to `logs` (level/message/context).
- Retries: DB reads are retried 3x with exponential backoff (Tenacity).

## Troubleshooting
- 401 with API_TOKEN set → ensure `Authorization: Bearer <token>`.
- 422 VALIDATION_ERROR → payload shape or types are wrong.
- Seed not applied → verify `db/seed.sql` exists and contains statements.
