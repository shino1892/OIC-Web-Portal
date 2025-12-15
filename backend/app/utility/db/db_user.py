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
        sql = """
            SELECT s.user_id, s.class_id, s.major_id, c.department_id 
            FROM student_users s
            JOIN classes c ON s.class_id = c.id
            WHERE s.google_sub = %s
        """
        with conn.cursor() as cursor:
            cursor.execute(sql, (google_sub,))
            return cursor.fetchone()
    except Exception as e:
        print(f"get_student_info error: {e}")
        return None
    finally:
        if conn:
            conn.close()

def register_user_card(user_id, idm):
    """
    学生のFeliCaカードを登録する（複数登録可）
    戻り値: "SUCCESS", "DUPLICATE", "DB_ERROR"
    """
    conn = None
    try:
        conn = db_connect()
        if not conn:
            return "DB_ERROR"
            
        # 重複チェック
        check_sql = "SELECT COUNT(*) as count FROM user_cards WHERE felica_idm = %s"
        with conn.cursor() as cursor:
            cursor.execute(check_sql, (idm,))
            result = cursor.fetchone()
            if result and result['count'] > 0:
                return "DUPLICATE"

        sql = "INSERT INTO user_cards (user_id, felica_idm) VALUES (%s, %s)"
        
        with conn.cursor() as cursor:
            cursor.execute(sql, (user_id, idm))
            conn.commit()
            return "SUCCESS"
            
    except Exception as e:
        print(f"register_user_card エラー: {e}", flush=True)
        return "DB_ERROR"

    finally:
        if conn:
            conn.close()

def get_user_cards(user_id):
    """
    学生の登録済みカード一覧を取得する
    """
    conn = None
    try:
        conn = db_connect()
        if not conn:
            return []
            
        sql = "SELECT felica_idm, registered_at FROM user_cards WHERE user_id = %s"
        
        with conn.cursor() as cursor:
            cursor.execute(sql, (user_id,))
            return cursor.fetchall()
            
    except Exception as e:
        print(f"get_user_cards エラー: {e}", flush=True)
        return []
    finally:
        if conn:
            conn.close()

def get_available_majors(department_id):
    try:
        conn = db_connect()
        sql = "SELECT id, name FROM major WHERE department_id = %s"
        with conn.cursor() as cursor:
            cursor.execute(sql, (department_id,))
            return cursor.fetchall()
    except Exception as e:
        print(f"get_available_majors error: {e}", flush=True)
        return []
    finally:
        if conn:
            conn.close()

def update_student_major(user_id, major_id):
    try:
        conn = db_connect()
        sql = "UPDATE student_users SET major_id = %s WHERE user_id = %s"
        with conn.cursor() as cursor:
            cursor.execute(sql, (major_id, user_id))
            conn.commit()
            return True
    except Exception as e:
        print(f"update_student_major error: {e}", flush=True)
        return False
    finally:
        if conn:
            conn.close()
