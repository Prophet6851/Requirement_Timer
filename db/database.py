import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "task.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
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
    # 初始化 XP 数据
    cursor.execute("INSERT OR IGNORE INTO gamification (key, value) VALUES ('xp', 0)")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized:", DB_PATH)