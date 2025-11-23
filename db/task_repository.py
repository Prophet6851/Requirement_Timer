# db/task_repository.py

from models.task import Task
from .database import get_connection

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
