import sqlite3
import os
from datetime import date
import flet as ft

# This function ensures the app can write data on Android
def get_db_path():
    # For Android APKs, we use the current working directory 
    # which Flet sets to the app's internal data folder.
    data_dir = os.getcwd() 
    return os.path.join(data_dir, "aspirantflow.db")

DB_PATH = get_db_path()


def _connect() -> sqlite3.Connection:
    """Return a connection with row_factory set so rows behave like dicts."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


class DatabaseManager:
    """
    Singleton-style class that owns every DB operation.
    Call DatabaseManager().method() from any module.
    """

    def __init__(self):
        self._init_tables()

    # ─────────────────────────────────────────────
    # Schema bootstrap
    # ─────────────────────────────────────────────

    def _init_tables(self):
        """Create all tables if they don't already exist."""
        ddl = """
        -- Users ---------------------------------------------------------
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT    UNIQUE NOT NULL,
            password_hash TEXT    NOT NULL,
            created_at    TEXT    DEFAULT (date('now'))
        );

        -- Daily Study Log -----------------------------------------------
        -- One row per (user, date, subject).
        CREATE TABLE IF NOT EXISTS study_logs (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL REFERENCES users(id),
            log_date   TEXT    NOT NULL,          -- ISO-8601: YYYY-MM-DD
            subject    TEXT    NOT NULL,          -- Physics / Chemistry / Biology
            hours      REAL    NOT NULL DEFAULT 0,
            topics     TEXT    DEFAULT ''
        );

        -- Backlog Manager ------------------------------------------------
        CREATE TABLE IF NOT EXISTS backlogs (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL REFERENCES users(id),
            topic      TEXT    NOT NULL,
            subject    TEXT    NOT NULL,
            priority   TEXT    NOT NULL DEFAULT 'Medium',  -- High/Medium/Low
            cleared    INTEGER NOT NULL DEFAULT 0,         -- 0=pending, 1=done
            created_at TEXT    DEFAULT (date('now'))
        );

        -- Test Analytics -------------------------------------------------
        CREATE TABLE IF NOT EXISTS test_marks (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL REFERENCES users(id),
            test_date  TEXT    NOT NULL,
            test_name  TEXT    DEFAULT '',
            physics    REAL    DEFAULT 0,
            chemistry  REAL    DEFAULT 0,
            biology    REAL    DEFAULT 0,
            total      REAL    DEFAULT 0
        );

        -- Daily To-Do (The Daily Grind) ----------------------------------
        CREATE TABLE IF NOT EXISTS todos (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL REFERENCES users(id),
            task       TEXT    NOT NULL,
            done       INTEGER NOT NULL DEFAULT 0,
            created_at TEXT    DEFAULT (date('now'))
        );

        -- Smart Timetable ------------------------------------------------
        -- Stores one slot per (user, day, slot_index).
        CREATE TABLE IF NOT EXISTS timetable (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL REFERENCES users(id),
            day        TEXT    NOT NULL,   -- Monday … Sunday
            slot_index INTEGER NOT NULL,
            time_label TEXT    NOT NULL,
            activity   TEXT    NOT NULL DEFAULT ''
        );

        -- Revision Notes -------------------------------------------------
        CREATE TABLE IF NOT EXISTS notes (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL REFERENCES users(id),
            title      TEXT    NOT NULL,
            body       TEXT    DEFAULT '',   -- Markdown content
            created_at TEXT    DEFAULT (date('now')),
            updated_at TEXT    DEFAULT (date('now'))
        );
        """
        with _connect() as conn:
            conn.executescript(ddl)

    # ─────────────────────────────────────────────
    # AUTH helpers (passwords handled in auth.py)
    # ─────────────────────────────────────────────

    def create_user(self, username: str, password_hash: str) -> bool:
        """Insert a new user. Returns False if username already taken."""
        try:
            with _connect() as conn:
                conn.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, password_hash),
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def get_user(self, username: str) -> dict | None:
        """Return user row as dict, or None if not found."""
        with _connect() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()
        return dict(row) if row else None

    # ─────────────────────────────────────────────
    # Study Log
    # ─────────────────────────────────────────────

    def upsert_study_log(self, user_id: int, log_date: str, subject: str,
                         hours: float, topics: str):
        """Insert or replace a study log entry for a given date+subject."""
        with _connect() as conn:
            existing = conn.execute(
                "SELECT id FROM study_logs WHERE user_id=? AND log_date=? AND subject=?",
                (user_id, log_date, subject),
            ).fetchone()
            if existing:
                conn.execute(
                    "UPDATE study_logs SET hours=?, topics=? WHERE id=?",
                    (hours, topics, existing["id"]),
                )
            else:
                conn.execute(
                    "INSERT INTO study_logs (user_id, log_date, subject, hours, topics) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (user_id, log_date, subject, hours, topics),
                )

    def get_study_logs(self, user_id: int, log_date: str) -> list[dict]:
        """Return all subject logs for a specific date."""
        with _connect() as conn:
            rows = conn.execute(
                "SELECT * FROM study_logs WHERE user_id=? AND log_date=? ORDER BY subject",
                (user_id, log_date),
            ).fetchall()
        return [dict(r) for r in rows]

    def get_recent_study_summary(self, user_id: int, days: int = 7) -> list[dict]:
        """Return daily total hours for the last N days (for dashboard)."""
        with _connect() as conn:
            rows = conn.execute(
                """SELECT log_date, SUM(hours) as total_hours
                   FROM study_logs
                   WHERE user_id=? AND log_date >= date('now', ?)
                   GROUP BY log_date ORDER BY log_date""",
                (user_id, f"-{days} days"),
            ).fetchall()
        return [dict(r) for r in rows]

    # ─────────────────────────────────────────────
    # Backlogs
    # ─────────────────────────────────────────────

    def add_backlog(self, user_id: int, topic: str, subject: str, priority: str) -> int:
        """Add a backlog item. Returns new row id."""
        with _connect() as conn:
            cur = conn.execute(
                "INSERT INTO backlogs (user_id, topic, subject, priority) VALUES (?, ?, ?, ?)",
                (user_id, topic, subject, priority),
            )
            return cur.lastrowid

    def get_backlogs(self, user_id: int, cleared: bool = False) -> list[dict]:
        with _connect() as conn:
            rows = conn.execute(
                "SELECT * FROM backlogs WHERE user_id=? AND cleared=? ORDER BY "
                "CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END",
                (user_id, 1 if cleared else 0),
            ).fetchall()
        return [dict(r) for r in rows]

    def toggle_backlog(self, item_id: int):
        with _connect() as conn:
            conn.execute(
                "UPDATE backlogs SET cleared = 1 - cleared WHERE id=?", (item_id,)
            )

    def delete_backlog(self, item_id: int):
        with _connect() as conn:
            conn.execute("DELETE FROM backlogs WHERE id=?", (item_id,))

    # ─────────────────────────────────────────────
    # Test Marks / Analytics
    # ─────────────────────────────────────────────

    def add_test(self, user_id: int, test_date: str, test_name: str,
                 physics: float, chemistry: float, biology: float) -> int:
        total = physics + chemistry + biology
        with _connect() as conn:
            cur = conn.execute(
                "INSERT INTO test_marks (user_id, test_date, test_name, physics, chemistry, biology, total) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (user_id, test_date, test_name, physics, chemistry, biology, total),
            )
            return cur.lastrowid

    def get_tests(self, user_id: int) -> list[dict]:
        with _connect() as conn:
            rows = conn.execute(
                "SELECT * FROM test_marks WHERE user_id=? ORDER BY test_date",
                (user_id,),
            ).fetchall()
        return [dict(r) for r in rows]

    def delete_test(self, test_id: int):
        with _connect() as conn:
            conn.execute("DELETE FROM test_marks WHERE id=?", (test_id,))

    # ─────────────────────────────────────────────
    # Daily To-Do
    # ─────────────────────────────────────────────

    def add_todo(self, user_id: int, task: str) -> int:
        with _connect() as conn:
            cur = conn.execute(
                "INSERT INTO todos (user_id, task) VALUES (?, ?)", (user_id, task)
            )
            return cur.lastrowid

    def get_todos(self, user_id: int) -> list[dict]:
        """Return all pending + today's done tasks."""
        with _connect() as conn:
            rows = conn.execute(
                "SELECT * FROM todos WHERE user_id=? ORDER BY done ASC, id ASC",
                (user_id,),
            ).fetchall()
        return [dict(r) for r in rows]

    def toggle_todo(self, todo_id: int):
        with _connect() as conn:
            conn.execute(
                "UPDATE todos SET done = 1 - done WHERE id=?", (todo_id,)
            )

    def delete_todo(self, todo_id: int):
        with _connect() as conn:
            conn.execute("DELETE FROM todos WHERE id=?", (todo_id,))

    # ─────────────────────────────────────────────
    # Timetable
    # ─────────────────────────────────────────────

    def save_timetable_slot(self, user_id: int, day: str, slot_index: int,
                            time_label: str, activity: str):
        with _connect() as conn:
            existing = conn.execute(
                "SELECT id FROM timetable WHERE user_id=? AND day=? AND slot_index=?",
                (user_id, day, slot_index),
            ).fetchone()
            if existing:
                conn.execute(
                    "UPDATE timetable SET time_label=?, activity=? WHERE id=?",
                    (time_label, activity, existing["id"]),
                )
            else:
                conn.execute(
                    "INSERT INTO timetable (user_id, day, slot_index, time_label, activity) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (user_id, day, slot_index, time_label, activity),
                )

    def get_timetable(self, user_id: int) -> list[dict]:
        with _connect() as conn:
            rows = conn.execute(
                "SELECT * FROM timetable WHERE user_id=? ORDER BY slot_index",
                (user_id,),
            ).fetchall()
        return [dict(r) for r in rows]

    # ─────────────────────────────────────────────
    # Revision Notes
    # ─────────────────────────────────────────────

    def add_note(self, user_id: int, title: str, body: str) -> int:
        with _connect() as conn:
            cur = conn.execute(
                "INSERT INTO notes (user_id, title, body) VALUES (?, ?, ?)",
                (user_id, title, body),
            )
            return cur.lastrowid

    def update_note(self, note_id: int, title: str, body: str):
        with _connect() as conn:
            conn.execute(
                "UPDATE notes SET title=?, body=?, updated_at=date('now') WHERE id=?",
                (title, body, note_id),
            )

    def get_notes(self, user_id: int) -> list[dict]:
        with _connect() as conn:
            rows = conn.execute(
                "SELECT * FROM notes WHERE user_id=? ORDER BY updated_at DESC",
                (user_id,),
            ).fetchall()
        return [dict(r) for r in rows]

    def delete_note(self, note_id: int):
        with _connect() as conn:
            conn.execute("DELETE FROM notes WHERE id=?", (note_id,))
