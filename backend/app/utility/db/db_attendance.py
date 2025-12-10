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

def get_subject_attendance_summary(user_id):
    """
    科目ごとの出席状況を取得する
    """
    conn = None
    try:
        conn = db_connect()
        if not conn:
            return []
            
        sql = """
            SELECT 
                s.name as subject_name,
                SUM(CASE WHEN a.status = '出席' THEN 1 ELSE 0 END) as present,
                SUM(CASE WHEN a.status = '欠席' THEN 1 ELSE 0 END) as absent,
                SUM(CASE WHEN a.status = '遅刻' THEN 1 ELSE 0 END) as late,
                SUM(CASE WHEN a.status = '早退' THEN 1 ELSE 0 END) as early,
                SUM(CASE WHEN a.status = '公欠' THEN 1 ELSE 0 END) as public_absent,
                COUNT(*) as total
            FROM attendance a
            JOIN timetables t ON a.timetable_id = t.id
            JOIN subjects s ON t.subject_id = s.id
            WHERE a.user_id = %s
            GROUP BY s.name
        """
        
        with conn.cursor() as cursor:
            cursor.execute(sql, (user_id,))
            return cursor.fetchall()
            
    except Exception as e:
        print(f"get_subject_attendance_summary エラー: {e}", flush=True)
        return []
    finally:
        if conn:
            conn.close()

def get_recent_attendance_history(user_id, limit=5):
    """
    直近の活動履歴（出席以外）を取得する
    """
    conn = None
    try:
        conn = db_connect()
        if not conn:
            return []
            
        sql = """
            SELECT 
                t.date,
                t.period,
                s.name as subject_name,
                a.status,
                a.reason,
                a.marked_at
            FROM attendance a
            JOIN timetables t ON a.timetable_id = t.id
            JOIN subjects s ON t.subject_id = s.id
            WHERE a.user_id = %s AND a.status != '出席'
            ORDER BY t.date DESC, t.period DESC
            LIMIT %s
        """
        
        with conn.cursor() as cursor:
            cursor.execute(sql, (user_id, limit))
            return cursor.fetchall()
            
    except Exception as e:
        print(f"get_recent_attendance_history エラー: {e}", flush=True)
        return []
    finally:
        if conn:
            conn.close()

