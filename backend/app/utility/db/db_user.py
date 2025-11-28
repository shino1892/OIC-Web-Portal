from app.utility.db.db_connect import db_connect

def exists_student_user(google_sub):
    conn = db_connect() 
    sql ="""
        SELECT EXIST(
            SELECT user_id
            FROM student_users
            WHERE google_sub =  %s
        ) AS user_exists;
        """

    try:
        with conn.cursor() as cursor:
            cursor.excute(sql,(google_sub,))
            result = cursor.fetchone()
            return result["user_exists"] == 1

    finally:
        conn.close()

def regist_student_user(user_id, email, google_sub, admission_year, fulll_name, class_id):
    conn = db_connect()
    sql = """
        INSERT INTO student_users (user_id,email,google_sub,admission_year,full_name, class_id) VALUES
            (%s,%s,%s,%s,%s)
    """

    try:
        with conn.cursor() as cursor:
            cursor.execute(sql,(user_id,email,google_sub,admission_year,fulll_name,class_id))
            return True
    except:
        return False
    finally:
        conn.close()       