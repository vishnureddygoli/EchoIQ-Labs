from collections.abc import Iterable
from contextlib import contextmanager
from typing import Any
import psycopg
from psycopg.rows import dict_row
from .config import get_settings

@contextmanager
def get_connection():
    with psycopg.connect(get_settings().database_url, row_factory=dict_row) as conn:
        yield conn

def fetch_one(query: str, params: Iterable[Any] | dict[str, Any] = ()) -> dict[str, Any] | None:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(query, params)
        return cur.fetchone()

def fetch_all(query: str, params: Iterable[Any] | dict[str, Any] = ()) -> list[dict[str, Any]]:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(query, params)
        return list(cur.fetchall())

def execute(query: str, params: Iterable[Any] | dict[str, Any] = ()) -> None:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(query, params)
        conn.commit()

def database_health() -> str:
    try:
        row = fetch_one("SELECT 1 AS ok")
        return "ok" if row and row["ok"] == 1 else "error"
    except Exception:
        return "error"
