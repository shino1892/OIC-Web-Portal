from app.utility.db.db_connect import db_connect

def register_attendance(user_id, timetable_id, status='出席'):
    """
    出席を登録する
    """
    conn = None
    try:
        conn = db_connect()
        if not conn:
            return False
            
        # 既に登録済みか確認（オプション）
        check_sql = "SELECT id FROM attendance WHERE user_id = %s AND timetable_id = %s"
        
        with conn.cursor() as cursor:
            cursor.execute(check_sql, (user_id, timetable_id))
            if cursor.fetchone():
                # 既に登録済みなら更新するか、無視するか。ここでは更新とするか、あるいはTrueを返して終了
                # 今回は重複登録を防ぐため、何もしないでTrueを返す
                return True

        sql = "INSERT INTO attendance (user_id, timetable_id, status) VALUES (%s, %s, %s)"
        
        with conn.cursor() as cursor:
            cursor.execute(sql, (user_id, timetable_id, status))
            conn.commit()
            return True
            
    except Exception as e:
        print(f"register_attendance エラー: {e}", flush=True)
        return False

    finally:
        if conn:
            conn.close()

def update_attendance_status(user_id, timetable_id, status, reason=None):
    """
    出席ステータスを更新する（または新規登録）
    """
    conn = None
    try:
        conn = db_connect()
        if not conn:
            return False
            
        # Check if exists
        check_sql = "SELECT id FROM attendance WHERE user_id = %s AND timetable_id = %s"
        
        with conn.cursor() as cursor:
            cursor.execute(check_sql, (user_id, timetable_id))
            result = cursor.fetchone()
            
            if result:
                # Update
                if reason:
                    update_sql = "UPDATE attendance SET status = %s, reason = %s, marked_at = CURRENT_TIMESTAMP WHERE id = %s"
                    cursor.execute(update_sql, (status, reason, result['id']))
                else:
                    update_sql = "UPDATE attendance SET status = %s, marked_at = CURRENT_TIMESTAMP WHERE id = %s"
                    cursor.execute(update_sql, (status, result['id']))
            else:
                # Insert
                if reason:
                    insert_sql = "INSERT INTO attendance (user_id, timetable_id, status, reason) VALUES (%s, %s, %s, %s)"
                    cursor.execute(insert_sql, (user_id, timetable_id, status, reason))
                else:
                    insert_sql = "INSERT INTO attendance (user_id, timetable_id, status) VALUES (%s, %s, %s)"
                    cursor.execute(insert_sql, (user_id, timetable_id, status))
                
            conn.commit()
            return True
            
    except Exception as e:
        print(f"update_attendance_status エラー: {e}", flush=True)
        return False

    finally:
        if conn:
            conn.close()

def get_attendance_summary(user_id):
    """
    出席率などのサマリーを取得する
    """
    conn = None
    try:
        conn = db_connect()
        if not conn:
            return None
            
        sql = """
            SELECT 
                status, 
                COUNT(*) as count 
            FROM attendance 
            WHERE user_id = %s 
            GROUP BY status
        """
        
        with conn.cursor() as cursor:
            cursor.execute(sql, (user_id,))
            results = cursor.fetchall()
            
            summary = {
                '出席': 0,
                '欠席': 0,
                '遅刻': 0,
                '早退': 0,
                '公欠': 0,
                'total': 0
            }
            
            for row in results:
                status = row['status']
                count = row['count']
                if status in summary:
                    summary[status] = count
                    summary['total'] += count
                    
            return summary
            
    except Exception as e:
        print(f"get_attendance_summary エラー: {e}", flush=True)
        return None

    finally:
        if conn:
            conn.close()

