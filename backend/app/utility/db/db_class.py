from app.utility.db.db_connect import db_connect

def get_class_data(department_id):
    try:
        conn = db_connect()
        sql = """ 
            SELECT *
            FROM classes
            WHERE department_id = %s
            """
        with conn.cursor() as cursor:
            cursor.execute(sql,(department_id))
            class_data = cursor.fetchone()
            return class_data["id"]
        
    finally:
        if conn:
            conn.close()
        