import sys
import os

# 如果直接运行此文件，将父目录加入路径以支持导入
if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.task import Task

try:
    from .database import get_connection
except ImportError:
    # 当作为脚本运行时，只能使用绝对导入（需结合 sys.path）
    from db.database import get_connection

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
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, module, version, status, priority,
               plan_start, plan_end, notes
        FROM task
        ORDER BY plan_end ASC;
    """)
    rows = cursor.fetchall()
    conn.close()
    return [row_to_task(r) for r in rows]

def create_task(task: Task):
    conn = get_connection()
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
    conn.close()

def update_task(task: Task):
    conn = get_connection()
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
    conn.close()

def delete_task(task_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM task WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def update_task_status(task_id: int, new_status: str):
    """只更新任务状态（用于归档移出等场景）"""
    conn = get_connection()
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
    conn.close()


def get_xp() -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT value FROM gamification WHERE key = 'xp'")
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0


def add_xp(amount: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE gamification SET value = value + ? WHERE key = 'xp'", (amount,))
    conn.commit()
    conn.close()


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
