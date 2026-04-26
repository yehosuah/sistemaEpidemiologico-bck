# AWS ECS Fargate Deployment Notes

Initial target: containerized FastAPI on ECS Fargate, PostgreSQL on RDS, public traffic through an Application Load Balancer.

## Runtime

- Build image from `Dockerfile`.
- Run `alembic upgrade head` before starting the API container.
- Expose container port `8000`.
- Configure ALB health check path as `/health`.
- Store secrets in AWS Secrets Manager or SSM Parameter Store.

## Required Environment

- `DATABASE_URL`: RDS PostgreSQL URL using `postgresql+psycopg://`.
- `JWT_SECRET`: high-entropy secret.
- `COOKIE_SECURE=true`.
- `CORS_ORIGINS`: comma-separated frontend origins.
- `AUTO_CREATE_MANAGER=true` only for first boot or controlled bootstrap.
- `MANAGER_EMAIL` and `MANAGER_PASSWORD` for bootstrap.

## Suggested AWS Shape

- ECS cluster with one Fargate service for the API.
- RDS PostgreSQL in private subnets.
- ALB in public subnets.
- API task in private subnets with outbound NAT if needed.
- Security group from ALB to API on `8000`.
- Security group from API to RDS on `5432`.
- CloudWatch logs for app container stdout/stderr.
