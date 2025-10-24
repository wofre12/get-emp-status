#!/usr/bin/env bash
set -euo pipefail
export PYTHONUNBUFFERED=1
python -m app.main --init-db
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload