from app.db.seed import ensure_manager
from app.db.session import SessionLocal


def main() -> None:
    db = SessionLocal()
    try:
        user = ensure_manager(db)
        if user is None:
            raise SystemExit("MANAGER_EMAIL and MANAGER_PASSWORD must be set.")
        print(f"Manager ready: {user.email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
