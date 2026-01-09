from __future__ import annotations

from app.utility.db.db_connect import db_connect


def list_notifications_for_student(user_id: int, department_id: int | None, class_id: int | None, major_id: int | None, limit: int = 100):
    """Return notifications visible to the given student along with per-user read state."""
    conn = db_connect()
    if not conn:
        return []

    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT
                    n.id,
                    n.type,
                    n.message,
                    n.scope,
                    n.target_user_id,
                    n.department_id,
                    n.class_id,
                    n.major_id,
                    COALESCE(r.is_read, FALSE) AS is_read,
                    r.read_at,
                    n.created_at
                FROM notifications n
                LEFT JOIN notification_reads r
                    ON r.notification_id = n.id AND r.user_id = %s
                WHERE
                    (n.scope = 'ALL')
                    OR (n.scope = 'USER' AND n.target_user_id = %s)
                    OR (n.scope = 'DEPARTMENT' AND n.department_id = %s)
                    OR (
                        n.scope = 'CLASS'
                        AND n.class_id = %s
                        AND (n.major_id IS NULL OR n.major_id = %s)
                    )
                ORDER BY n.created_at DESC
                LIMIT %s
            """
            cursor.execute(sql, (user_id, user_id, department_id, class_id, major_id, limit))
            return cursor.fetchall()

    except Exception as e:
        print(f"list_notifications_for_student error: {e}")
        return []
    finally:
        conn.close()


def mark_notification_read(user_id: int, notification_id: int) -> bool:
    conn = db_connect()
    if not conn:
        return False

    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO notification_reads (notification_id, user_id, is_read, read_at)
                VALUES (%s, %s, TRUE, NOW())
                ON DUPLICATE KEY UPDATE is_read = TRUE, read_at = NOW()
            """
            cursor.execute(sql, (notification_id, user_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"mark_notification_read error: {e}")
        try:
            conn.rollback()
        except Exception:
            pass
        return False
    finally:
        conn.close()


def create_notification(
    *,
    notif_type: str,
    message: str,
    scope: str,
    target_user_id: int | None = None,
    department_id: int | None = None,
    class_id: int | None = None,
    major_id: int | None = None,
) -> int | None:
    """Create a notification and return its id."""
    conn = db_connect()
    if not conn:
        return None

    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO notifications (type, message, scope, target_user_id, department_id, class_id, major_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (notif_type, message, scope, target_user_id, department_id, class_id, major_id))
            notification_id = cursor.lastrowid
        conn.commit()
        return notification_id
    except Exception as e:
        print(f"create_notification error: {e}")
        try:
            conn.rollback()
        except Exception:
            pass
        return None
    finally:
        conn.close()
