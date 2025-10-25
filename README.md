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
- Bonus: TTL cache, DB logger, DB retries, bearer-token protection (**required**)

## API
### Request
```http
POST /api/GetEmpStatus
Content-Type: application/json
Authorization: Bearer <token>        # REQUIRED
```
Body:
```json
{ "NationalNumber": "NAT1001" }
```

### Successful Response (200)
```json
{
  "EmployeeName": "John Doe",
  "NationalNumber": "NAT1001",
  "HighestSalary": 2500,
  "AverageSalary": 1870.45,
  "Status": "GREEN",
  "IsActive": true,
  "LastUpdated": "2025-10-24T18:12:04Z"
}
```

## Business Rules
- Monthly adjustments:
  - **December**: +10%
  - **June–August**: –5%
- Tax: If adjusted **total > 10,000**, apply **7%** deduction to the **total**.
- Status uses the **post-tax average** (`averageAfterTax`):
  - `> 2000` → **GREEN**
  - `= 2000` → **ORANGE**
  - `< 2000` → **RED**
- Requires **at least 3** salary rows for active users.
```
> **Output notes:**  
> - `HighestSalary` is computed from month-adjusted values (pre-tax).  
> - `AverageSalary` is the post-tax average (7% deduction applied to total when sum > 10,000), rounded to 2 decimals.  
> - `LastUpdated` is UTC ISO-8601 and ends with `Z`.
```

## Errors
All business/HTTP errors are returned as:
```json
{ "error": "<message>" }
```

Typical cases:
- `404` — `{ "error": "Invalid National Number" }`
- `406` — `{ "error": "User is not Active" }`
- `422` — `{ "error": "INSUFFICIENT_DATA" }` (active user with <3 salary rows)
- `401` — `{ "error": "Unauthorized" }` (missing/invalid Bearer token)


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
| `API_TOKEN` | *(required)* | Bearer token all requests must present. |
| `CACHE_TTL_SECONDS` | `60` | Cache TTL seconds for employee responses |
| `LOG_TO_DB` | `1` | `1` to enable DB logging to `logs` table |

## Run Locally
```bash
python -m venv .venv
source .venv/bin/activate           # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# REQUIRED: set API token before starting the server
export API_TOKEN="secret123"        # Windows (PowerShell): $env:API_TOKEN="secret123"
uvicorn app.main:app --reload
```
Open Swagger UI at `http://localhost:8000/docs`.

## Testing
```bash
pytest -vv --log-cli-level=INFO
```

## Postman Collection
Import `postman/GetEmpStatus.postman_collection.json`. The request inherits Bearer auth automatically.

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

### Core Classes & Responsibilities
- **ProcessStatus** — business logic orchestration (month adjustments, tax rule, metrics, status).
- **DataAccess** — all DB interactions (queries/transactions) with retry.
- **EmpInfo** — employee view model for API/logic.
- **Validator** — bearer token validation (401 on missing/invalid token).

## Data Model & Seed
See `db/seed.sql` for sample users/salaries. The app loads it at startup (idempotent).

## Caching, Logging, Retries
- Caching: key = `empstatus:<nationalNumber>`, TTL=`CACHE_TTL_SECONDS`. Bypass by adding `?bustCache=true` to the request URL.
- Logging: each call writes decision context to `logs` (level/message/context).
- Retries: DB reads are retried 3x with exponential backoff (Tenacity).

## Troubleshooting
- 401 → ensure you sent `Authorization: Bearer <token>` and that it matches `API_TOKEN`.
- 422 VALIDATION_ERROR → payload shape or types are wrong.
- Seed not applied → verify `db/seed.sql` exists and contains statements.
