# sistemaEpidemiologico Backend

FastAPI backend scaffold for manager auth and public screen availability management.

## Stack

- Python 3.11-3.13
- FastAPI REST API
- PostgreSQL
- SQLAlchemy 2
- Alembic migrations
- JWT bearer auth plus secure HTTP-only cookies

## Local Run

Create `.env` from `.env.example` and make sure PostgreSQL is running locally with the
database URL configured in that file.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload
```

The API runs at `http://127.0.0.1:8000`.

This repo currently targets Python 3.11 through 3.13. If `python3 --version`
prints Python 3.14, use a Python 3.12 or 3.13 interpreter when creating `.venv`.

API:

- `GET /health`
- `GET /api/v1/health`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`
- `GET /api/v1/public/screens`
- `GET /api/v1/management/screens`
- `POST /api/v1/management/screens`
- `PATCH /api/v1/management/screens/{key}`

## Access Model

Roles are intentionally not part of this backend.

Public visitors do not need accounts. Manager accounts are the only authenticated users in v1, and every manager can access all protected management activities.

Public screen availability is stored in the database. The public API returns only enabled screens; managers can create and toggle all screen records.

## Manager Bootstrap

Set these variables and run the service or script:

```bash
AUTO_CREATE_MANAGER=true
MANAGER_EMAIL=manager@example.com
MANAGER_PASSWORD=ChangeMe123!
```

Manual bootstrap:

```bash
python scripts/create_manager.py
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```
