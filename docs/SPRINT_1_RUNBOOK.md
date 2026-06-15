# Sprint 1 Runbook

## Local setup

```bash
cp .env.example .env
docker compose up -d
```

PostgreSQL is exposed on `localhost:5432` and Redis on `localhost:6379`. The initial schema is mounted from `packages/db/migrations/0001_initial.sql` when the database volume is first created.

## API

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload --port 8000
```

## Worker

```bash
cd apps/worker
python -m venv .venv
source .venv/bin/activate
pip install -e .
python app/main.py
```

## Web dashboard

```bash
pnpm install
pnpm dev
```

Open `http://localhost:3000`. If the API is unavailable, the dashboard may show demo fallback data, but the UI must clearly display an `API unavailable. Showing demo fallback data.` warning banner so fallback data is never mistaken for live metrics.

## Test curl commands

Health check:

```bash
curl http://localhost:8000/health
```

Create website lead:

```bash
curl -X POST http://localhost:8000/webhooks/website \
  -H "Content-Type: application/json" \
  -d '{"name":"John Miller","phone":"+15125550123","email":"john@example.com","country":"USA","city":"Austin","language_preference":"english","source_platform":"website","campaign_name":"Storm Damage Roof Inspection","offer_name":"Free roof inspection","consent_status":"provided"}'
```

List leads:

```bash
curl http://localhost:8000/leads
```

Dashboard metrics:

```bash
curl http://localhost:8000/leads/metrics/summary
```

## Expected results

- `/health` returns `api`, `database`, and `redis` statuses.
- Lead creation returns a `lead_id`, a `call_attempt_id`, score `10`, and `queued: true`.
- Redis receives a job in `echoiq:outbound_calls`.
- The worker prints the job and updates the call attempt to `dispatched_mock`.
- The dashboard shows lead totals and the recent lead table.
