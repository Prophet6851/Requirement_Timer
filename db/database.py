import os
import sqlite3
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "task.db")

@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS task (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            module TEXT,
            version TEXT,
            status TEXT NOT NULL,
            priority TEXT NOT NULL,
            plan_start TEXT,
            plan_end TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 游戏化 XP 表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS gamification (
            key TEXT PRIMARY KEY,
            value INTEGER DEFAULT 0
        );
        """)
        # 鍒濆鍖?XP 鏁版嵁
        cursor.execute("INSERT OR IGNORE INTO gamification (key, value) VALUES ('xp', 0)")

        conn.commit()


if __name__ == "__main__":
    init_db()
    print("Database initialized:", DB_PATH)