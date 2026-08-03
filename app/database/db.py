import json
import os
import sqlite3
from contextlib import contextmanager
from typing import Any, Iterator, Optional

_SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

_db_path: str = "data/ai_estimate.db"


def init_db(database_path: str) -> None:
    global _db_path
    _db_path = database_path
    os.makedirs(os.path.dirname(database_path) or ".", exist_ok=True)
    with _connect() as conn:
        with open(_SCHEMA_PATH, "r", encoding="utf-8") as schema_file:
            conn.executescript(schema_file.read())


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    conn = _connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def get_or_create_user(telegram_id: int, username: Optional[str]) -> int:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id FROM users WHERE telegram_id = ?", (telegram_id,)
        ).fetchone()
        if row:
            return row["id"]
        cursor = conn.execute(
            "INSERT INTO users (telegram_id, username) VALUES (?, ?)",
            (telegram_id, username),
        )
        return cursor.lastrowid


def save_price_list(user_id: int, filename: str, items: list[dict[str, Any]]) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO price_lists (user_id, filename) VALUES (?, ?)",
            (user_id, filename),
        )
        price_list_id = cursor.lastrowid
        conn.executemany(
            """
            INSERT INTO price_items (price_list_id, code, name, unit, work_price, material_price)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    price_list_id,
                    item.get("code"),
                    item["name"],
                    item["unit"],
                    item.get("work_price", 0),
                    item.get("material_price", 0),
                )
                for item in items
            ],
        )
        return price_list_id


def get_price_items(price_list_id: int) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT code, name, unit, work_price, material_price FROM price_items WHERE price_list_id = ?",
            (price_list_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def create_project(user_id: int, price_list_id: Optional[int], survey: dict[str, Any]) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO projects (user_id, price_list_id, survey_json) VALUES (?, ?, ?)",
            (user_id, price_list_id, json.dumps(survey, ensure_ascii=False)),
        )
        return cursor.lastrowid


def add_project_file(project_id: int, file_path: str, file_type: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO project_files (project_id, file_path, file_type) VALUES (?, ?, ?)",
            (project_id, file_path, file_type),
        )


def get_project_files(project_id: int) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT file_path, file_type FROM project_files WHERE project_id = ?",
            (project_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def save_estimate(
    project_id: int,
    analysis: dict[str, Any],
    calculation: dict[str, Any],
    recommendations: list[str],
) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO estimates (project_id, analysis_json, calculation_json, recommendations_json)
            VALUES (?, ?, ?, ?)
            """,
            (
                project_id,
                json.dumps(analysis, ensure_ascii=False),
                json.dumps(calculation, ensure_ascii=False),
                json.dumps(recommendations, ensure_ascii=False),
            ),
        )
        return cursor.lastrowid


def log_request(telegram_id: Optional[int], action: str, payload: Optional[str] = None) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO request_log (telegram_id, action, payload) VALUES (?, ?, ?)",
            (telegram_id, action, payload),
        )
