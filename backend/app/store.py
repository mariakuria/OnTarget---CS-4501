import sqlite3
import threading
from typing import Optional

from app.models import Plan


class InMemoryStore:
    def __init__(self):
        self._plans: dict[str, Plan] = {}

    def save(self, plan: Plan) -> None:
        self._plans[plan.id] = plan

    def get(self, plan_id: str) -> Optional[Plan]:
        return self._plans.get(plan_id)


class SqliteStore:
    """Stores each plan as one JSON document. Safe to call from FastAPI's worker threads."""

    def __init__(self, path: str = "ontarget.db"):
        self._lock = threading.Lock()
        self._db = sqlite3.connect(path, check_same_thread=False)
        self._db.execute("CREATE TABLE IF NOT EXISTS plans (id TEXT PRIMARY KEY, data TEXT NOT NULL)")
        self._db.commit()

    def save(self, plan: Plan) -> None:
        with self._lock:
            self._db.execute(
                "INSERT INTO plans (id, data) VALUES (?, ?) "
                "ON CONFLICT(id) DO UPDATE SET data = excluded.data",
                (plan.id, plan.model_dump_json()),
            )
            self._db.commit()

    def get(self, plan_id: str) -> Optional[Plan]:
        with self._lock:
            row = self._db.execute("SELECT data FROM plans WHERE id = ?", (plan_id,)).fetchone()
        return Plan.model_validate_json(row[0]) if row else None
