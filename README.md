# sistemaEpidemiologico Backend

FastAPI backend scaffold for manager auth and public screen availability management.

## Stack

- Python 3.11+
- FastAPI REST API
- PostgreSQL
- SQLAlchemy 2
- Alembic migrations
- JWT bearer auth plus secure HTTP-only cookies
- Docker Compose for local development

## Local Run

Create `.env` from `.env.example`, then run:

```bash
docker compose up --build
```

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
python -m pytest
```

## AWS

Deployment target is ECS Fargate with RDS PostgreSQL. See `docs/aws-ecs-fargate.md`.
