from app.utility.db.db_connect import db_connect

def exists_student_user(google_sub):

    try:
        conn = db_connect() 
        sql ="""
            SELECT EXIST(
                SELECT user_id
                FROM student_users
                WHERE google_sub =  %s
            ) AS user_exists;
            """
        with conn.cursor() as cursor:
            cursor.excute(sql,(google_sub,))
            result = cursor.fetchone()
            return result["user_exists"] == 1

    except:
        return False

    finally:
        if conn:
            conn.close()

def exists_teacher_user(email,google_sub):

    try:
        conn = db_connect() 
        select_sql = """
                SELECT user_id, google_sub
                FROM teacher_users
                WHERE email = %s;
                """
        with conn.cursor() as cursor:
            cursor.excute(select_sql,(email,))
            user_record = cursor.fetchone()

            user_exists = user_record is not None

            if user_exists:
                db_google_sub = user_record.get('google_sub')

                if not db_google_sub:

                    update_sql = """
                    UPDATE teacher_users
                    SET google_sub = %s
                    WHERE email = %s;
                    """

                    cursor.execute(update_sql,(google_sub,email))
                    conn.commit()
            return user_exists
    except:
        if conn:
            conn.rollback() 
        # エラー発生時の適切な処理（例：例外を再スロー、ログ記録など）
        raise

    finally:
        if conn:
            conn.close()

def regist_student_user(user_id, email, google_sub, admission_year, fulll_name, class_id):

    try:
        conn = db_connect()
        sql = """
            INSERT INTO student_users (user_id,email,google_sub,admission_year,full_name, class_id) VALUES
                (%s,%s,%s,%s,%s)
        """
        with conn.cursor() as cursor:
            cursor.execute(sql,(user_id,email,google_sub,admission_year,fulll_name,class_id))
            return True
    except:
        return False
    finally:
        if conn:
            conn.close()
        