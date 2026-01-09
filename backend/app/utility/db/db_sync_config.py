from __future__ import annotations

from app.utility.db.db_connect import db_connect


def list_enabled_department_spreadsheets():
    conn = db_connect()
    if not conn:
        return []

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT department_id, spreadsheet_id, worksheet_name
                FROM department_spreadsheets
                WHERE enabled = TRUE
                ORDER BY department_id
                """
            )
            return cursor.fetchall()
    except Exception as e:
        print(f"list_enabled_department_spreadsheets error: {e}")
        return []
    finally:
        conn.close()


def resolve_major_id_by_alias(department_id: int, alias_name: str):
    """Resolve major_id from an alias in a specific department.

    Strategy:
    1) major_aliases (alias_name -> canonical_major_name)
    2) direct match to major.name
    """
    conn = db_connect()
    if not conn:
        return None

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT canonical_major_name
                FROM major_aliases
                WHERE department_id = %s AND alias_name = %s
                """,
                (department_id, alias_name),
            )
            row = cursor.fetchone()
            canonical = row["canonical_major_name"] if row else None

            if canonical:
                cursor.execute(
                    """
                    SELECT id
                    FROM major
                    WHERE department_id = %s AND name = %s
                    """,
                    (department_id, canonical),
                )
                m = cursor.fetchone()
                return m["id"] if m else None

            cursor.execute(
                """
                SELECT id
                FROM major
                WHERE department_id = %s AND name = %s
                """,
                (department_id, alias_name),
            )
            m2 = cursor.fetchone()
            return m2["id"] if m2 else None

    except Exception as e:
        print(f"resolve_major_id_by_alias error: {e}")
        return None
    finally:
        conn.close()


def resolve_class_id(department_id: int, grade: int):
    conn = db_connect()
    if not conn:
        return None

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id
                FROM classes
                WHERE department_id = %s AND grade = %s
                LIMIT 1
                """,
                (department_id, grade),
            )
            row = cursor.fetchone()
            return row["id"] if row else None
    except Exception as e:
        print(f"resolve_class_id error: {e}")
        return None
    finally:
        conn.close()
