from __future__ import annotations

from app.utility.db.db_connect import db_connect


def get_last_success_at(department_id: int):
    conn = db_connect()
    if not conn:
        return None

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT last_success_at
                FROM timetable_sync_runs
                WHERE department_id = %s
                """,
                (department_id,),
            )
            row = cursor.fetchone()
            return row["last_success_at"] if row else None
    except Exception as e:
        print(f"get_last_success_at error: {e}")
        return None
    finally:
        conn.close()


def upsert_sync_run(
    *,
    department_id: int,
    status: str,
    error_message: str | None = None,
    mark_success: bool = False,
):
    conn = db_connect()
    if not conn:
        return

    try:
        with conn.cursor() as cursor:
            if mark_success:
                cursor.execute(
                    """
                    INSERT INTO timetable_sync_runs (department_id, last_run_at, last_success_at, last_status, last_error)
                    VALUES (%s, NOW(), NOW(), %s, %s)
                    ON DUPLICATE KEY UPDATE
                        last_run_at = NOW(),
                        last_success_at = NOW(),
                        last_status = VALUES(last_status),
                        last_error = VALUES(last_error)
                    """,
                    (department_id, status, error_message),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO timetable_sync_runs (department_id, last_run_at, last_status, last_error)
                    VALUES (%s, NOW(), %s, %s)
                    ON DUPLICATE KEY UPDATE
                        last_run_at = NOW(),
                        last_status = VALUES(last_status),
                        last_error = VALUES(last_error)
                    """,
                    (department_id, status, error_message),
                )
        conn.commit()
    except Exception as e:
        print(f"upsert_sync_run error: {e}")
        try:
            conn.rollback()
        except Exception:
            pass
    finally:
        conn.close()
