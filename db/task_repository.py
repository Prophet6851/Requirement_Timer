import sys
import os

# 如果直接运行此文件，将父目录加入路径以支持导入
if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.task import Task

try:
    from .database import get_connection, get_db_connection
except ImportError:
    # 褰撲綔涓鸿剼鏈繍琛屾椂锛屽彧鑳戒娇鐢ㄧ粷瀵瑰鍏ワ紙闇€缁撳悎 sys.path锛?
    from db.database import get_connection, get_db_connection

def row_to_task(row):
    return Task(
        id=row[0],
        title=row[1],
        module=row[2],
        version=row[3],
        status=row[4],
        priority=row[5],
        plan_start=row[6],
        plan_end=row[7],
        notes=row[8],
    )

def list_tasks():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, module, version, status, priority,
                   plan_start, plan_end, notes
            FROM task
            ORDER BY plan_end ASC;
        """)
        rows = cursor.fetchall()
    return [row_to_task(r) for r in rows]

def create_task(task: Task):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO task (title, module, version, status, priority,
                              plan_start, plan_end, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task.title,
            task.module,
            task.version,
            task.status,
            task.priority,
            task.plan_start,
            task.plan_end,
            task.notes,
        ))
        conn.commit()

def update_task(task: Task):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE task
            SET title = ?, module = ?, version = ?, status = ?, priority = ?,
                plan_start = ?, plan_end = ?, notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            task.title, task.module, task.version, task.status, task.priority,
            task.plan_start, task.plan_end, task.notes, task.id
        ))
        conn.commit()

def delete_task(task_id: int):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM task WHERE id = ?", (task_id,))
        conn.commit()

def update_task_status(task_id: int, new_status: str):
    """鍙洿鏂颁换鍔＄姸鎬侊紙鐢ㄤ簬褰掓。绉诲嚭绛夊満鏅級"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE task
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (new_status, task_id)
        )
        conn.commit()


def get_xp() -> int:
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT value FROM gamification WHERE key = 'xp'")
        row = cur.fetchone()
    return row[0] if row else 0


def add_xp(amount: int):
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE gamification SET value = value + ? WHERE key = 'xp'", (amount,))
        conn.commit()

def get_level(xp: int) -> int:
    import math
    return math.floor(xp / 1000) + 1


if __name__ == "__main__":
    print("=== Testing Task Repository ===")
    try:
        current_xp = get_xp()
        print(f"Current XP: {current_xp}")
        print(f"Current Level: {get_level(current_xp)}")
    except Exception as e:
        print(f"Error accessing DB: {e}")
