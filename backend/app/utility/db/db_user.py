from app.utility.db.db_connect import db_connect

def exists_student_user(google_sub):
    try:
        conn = db_connect() 
        # EXISTSを使って存在確認を行う正しいSQL
        sql = "SELECT COUNT(*) FROM student_users WHERE google_sub = %s"
        
        with conn.cursor() as cursor:
            cursor.execute(sql, (google_sub,))
            result = cursor.fetchone()
            # COUNT(*)の結果を確認 (辞書型の場合はキーに注意、タプルの場合はインデックス)
            # PyMySQLのデフォルトカーソルはタプル、DictCursorなら辞書
            # db_connectの実装によるが、ここでは安全に判定
            if isinstance(result, dict):
                count = list(result.values())[0]
            else:
                count = result[0]
                
            return count > 0
        
    except Exception as e:
        print(f"exists_student_user エラー: {e}", flush=True)
        return False

    finally:
        if conn:
            conn.close()

def exists_teacher_user(email, google_sub):
    try:
        conn = db_connect() 
        select_sql = """
                SELECT user_id, google_sub
                FROM teacher_users
                WHERE email = %s;
                """
        with conn.cursor() as cursor:
            cursor.execute(select_sql, (email,))
            user_record = cursor.fetchone()

            user_exists = user_record is not None

            if user_exists:
                db_google_sub = user_record.get('google_sub') if isinstance(user_record, dict) else user_record[1]

                if not db_google_sub:
                    update_sql = """
                    UPDATE teacher_users
                    SET google_sub = %s
                    WHERE email = %s;
                    """
                    cursor.execute(update_sql, (google_sub, email))
                    conn.commit()
            
            return user_exists
    except Exception as e:
        print(f"exists_teacher_user エラー: {e}", flush=True)
        if conn:
            conn.rollback() 
        raise

    finally:
        if conn:
            conn.close()

def regist_student_user(user_id, email, google_sub, admission_year, full_name, class_id):
    try:
        conn = db_connect()
        # プレースホルダーの数を修正 (6個)
        sql = """
            INSERT INTO student_users (user_id, email, google_sub, admission_year, full_name, class_id) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        with conn.cursor() as cursor:
            cursor.execute(sql, (user_id, email, google_sub, admission_year, full_name, class_id))
            conn.commit() # コミットが必要
            return True
    except Exception as e:
        print(f"regist_student_user エラー: {e}", flush=True)
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def get_student_info(google_sub):
    """
    Google Sub IDから学生情報を取得する
    """
    try:
        conn = db_connect()
        sql = "SELECT user_id, class_id, major_id FROM student_users WHERE google_sub = %s"
        with conn.cursor() as cursor:
            cursor.execute(sql, (google_sub,))
            return cursor.fetchone()
    except Exception as e:
        print(f"get_student_info error: {e}")
        return None
    finally:
        if conn:
            conn.close()