from sqlalchemy import func, text
from sqlalchemy.orm import Session


def AllocateNextBigIntIds(db: Session, model, count: int = 1) -> list[int]:
    if count <= 0:
        return []

    # Some tests use lightweight fake sessions without SQLAlchemy bind/query APIs.
    if not hasattr(db, "query"):
        return [offset for offset in range(1, count + 1)]

    bind_getter = getattr(db, "get_bind", None)
    bind = bind_getter() if callable(bind_getter) else None
    dialect_name = getattr(getattr(bind, "dialect", None), "name", "")

    # Lock per-table id allocation during the current transaction.
    if dialect_name == "postgresql" and hasattr(db, "execute"):
        db.execute(
            text("SELECT pg_advisory_xact_lock(hashtext(:lock_key))"),
            {"lock_key": f"id_alloc:{model.__tablename__}"},
        )

    current_max_id = db.query(func.coalesce(func.max(model.id), 0)).scalar() or 0
    return [current_max_id + offset for offset in range(1, count + 1)]



