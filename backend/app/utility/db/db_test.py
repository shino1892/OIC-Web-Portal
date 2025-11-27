from app.utility.db.db_connect import db_connect

def get_departments():
    conn = db_connect()
    sql = "SELECT * FROM departments"
    with conn.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()

    return rows