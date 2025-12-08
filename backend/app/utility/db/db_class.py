from app.utility.db.db_connect import db_connect

def get_class_data(department_id, grade=1):
    try:
        conn = db_connect()
        sql = """ 
            SELECT *
            FROM classes
            WHERE department_id = %s AND grade = %s
            """
        with conn.cursor() as cursor:
            cursor.execute(sql, (department_id, grade))
            class_data = cursor.fetchone()
            if class_data:
                return class_data["id"]
            else:
                # Fallback: try to find any class for the department if specific grade not found
                # Or maybe create one? For now, just return None or try without grade
                sql_fallback = "SELECT * FROM classes WHERE department_id = %s LIMIT 1"
                cursor.execute(sql_fallback, (department_id,))
                fallback_data = cursor.fetchone()
                return fallback_data["id"] if fallback_data else None
        
    finally:
        if conn:
            conn.close()

def get_majors_by_department(department_id):
    try:
        conn = db_connect()
        sql = "SELECT id, name FROM major WHERE department_id = %s"
        with conn.cursor() as cursor:
            cursor.execute(sql, (department_id,))
            return cursor.fetchall()
    except Exception as e:
        print(f"get_majors_by_department error: {e}")
        return []
    finally:
        if conn:
            conn.close()
        