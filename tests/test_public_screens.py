from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password
from app.models.user import User


def create_user(db: Session, email: str, is_manager: bool) -> User:
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


def manager_token(db: Session) -> str:
    manager = create_user(db, "manager@example.com", is_manager=True)
    return create_access_token(manager.id, manager.is_manager)


def test_public_endpoint_returns_only_enabled_screens(
    client: TestClient,
    db_session: Session,
) -> None:
    token = manager_token(db_session)
    headers = {"Authorization": f"Bearer {token}"}

    enabled = client.post(
        "/api/v1/management/screens",
        headers=headers,
        json={"key": "dashboard", "title": "Dashboard", "enabled": True, "display_order": 2},
    )
    disabled = client.post(
        "/api/v1/management/screens",
        headers=headers,
        json={"key": "reports", "title": "Reports", "enabled": False, "display_order": 1},
    )
    assert enabled.status_code == 201
    assert disabled.status_code == 201

    response = client.get("/api/v1/public/screens")

    assert response.status_code == 200
    assert [screen["key"] for screen in response.json()] == ["dashboard"]


def test_unauthenticated_user_cannot_manage_screens(client: TestClient) -> None:
    response = client.post(
        "/api/v1/management/screens",
        json={"key": "dashboard", "title": "Dashboard"},
    )

    assert response.status_code == 401


def test_non_manager_cannot_manage_screens(client: TestClient, db_session: Session) -> None:
    user = create_user(db_session, "viewer@example.com", is_manager=False)
    token = create_access_token(user.id, user.is_manager)

    response = client.post(
        "/api/v1/management/screens",
        headers={"Authorization": f"Bearer {token}"},
        json={"key": "dashboard", "title": "Dashboard"},
    )

    assert response.status_code == 403


def test_manager_can_create_update_and_toggle_screen(
    client: TestClient,
    db_session: Session,
) -> None:
    token = manager_token(db_session)
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post(
        "/api/v1/management/screens",
        headers=headers,
        json={"key": "map", "title": "Map", "enabled": True, "display_order": 1},
    )
    assert created.status_code == 201
    assert created.json()["enabled"] is True

    updated = client.patch(
        "/api/v1/management/screens/map",
        headers=headers,
        json={"title": "Public Map", "enabled": False, "display_order": 5},
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "Public Map"
    assert updated.json()["enabled"] is False

    management = client.get("/api/v1/management/screens", headers=headers)
    assert [screen["key"] for screen in management.json()] == ["map"]

    public = client.get("/api/v1/public/screens")
    assert public.json() == []
