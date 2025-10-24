# GetEmpStatus Service

This service exposes a single endpoint that returns employee details and a computed status based on historical salaries. It is built with FastAPI and SQLAlchemy and ships with sample data for quick testing.

## Key features

- **Business rules**
  - Monthly adjustments:
    - December (+10%)
    - June–August (–5%)
    - Other months (no change)
  - If the total (after monthly adjustments) exceeds 10,000, a 7% deduction is applied to the total.
  - The average (after the total deduction, if any) determines the status:
    - Average > 2000 → `GREEN`
    - Average = 2000 → `ORANGE`
    - Average < 2000 → `RED`
- **Error handling**
  - `404` — invalid national number
  - `406` — user exists but is inactive
  - `422` — fewer than three salary records
- **Optional safeguards (enable via environment variables)**
  - Bearer token check: set `API_TOKEN`
  - Response caching with TTL (`CACHE_TTL_SECONDS`, default 60s) and `?bustCache=true`
  - Database retries using exponential backoff
  - Request/decision logs stored in the `logs` table

## Quick start

1. **Create a virtual environment and install dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate    # Windows: .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
