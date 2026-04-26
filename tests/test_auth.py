from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User


def create_user(db: Session, email: str, is_manager: bool = True) -> User:
    user = User(
        email=email,
        password_hash=hash_password("Password123!"),
        is_manager=is_manager,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_health(client: TestClient) -> None:
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/api/v1/health").json() == {"status": "ok"}


def test_manager_can_login(client: TestClient, db_session: Session) -> None:
    create_user(db_session, "manager@example.com")

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "manager@example.com", "password": "Password123!"},
    )

    assert login.status_code == 200
    payload = login.json()
    assert payload["token_type"] == "bearer"
    assert payload["user"]["email"] == "manager@example.com"
    assert payload["user"]["is_manager"] is True
    assert "se_access_token" in login.cookies
    assert "se_refresh_token" in login.cookies


def test_login_rejects_non_manager(client: TestClient, db_session: Session) -> None:
    create_user(db_session, "viewer@example.com", is_manager=False)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "viewer@example.com", "password": "Password123!"},
    )

    assert response.status_code == 403


def test_login_rejects_bad_password(client: TestClient, db_session: Session) -> None:
    create_user(db_session, "manager@example.com")

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "manager@example.com", "password": "wrong"},
    )

    assert response.status_code == 401


def test_refresh_rotates_and_revokes_old_token(client: TestClient, db_session: Session) -> None:
    create_user(db_session, "refresh@example.com")
    created = client.post(
        "/api/v1/auth/login",
        json={"email": "refresh@example.com", "password": "Password123!"},
    ).json()

    refreshed = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": created["refresh_token"]},
    )
    assert refreshed.status_code == 200

    reused_old = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": created["refresh_token"]},
    )
    assert reused_old.status_code == 401


def test_logout_revokes_refresh_token(client: TestClient, db_session: Session) -> None:
    create_user(db_session, "logout@example.com")
    created = client.post(
        "/api/v1/auth/login",
        json={"email": "logout@example.com", "password": "Password123!"},
    ).json()

    logout = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": created["refresh_token"]},
    )
    assert logout.status_code == 204

    refreshed = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": created["refresh_token"]},
    )
    assert refreshed.status_code == 401


def test_me_requires_auth(client: TestClient) -> None:
    assert client.get("/api/v1/auth/me").status_code == 401
