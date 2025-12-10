from app.utility.db.db_connect import db_connect

def get_timetable(class_id, major_id, start_date, end_date, user_id=None):
    """
    指定されたクラス、専攻、期間の時間割を取得する。
    major_idが指定されている場合は、その専攻の授業 + 共通授業(major_id IS NULL)を取得する。
    user_idが指定されている場合は、そのユーザーの出席ステータスも取得する。
    """
    conn = db_connect()
    if not conn:
        return []

    try:
        with conn.cursor() as cursor:
            # major_idがNoneの場合は共通授業のみ取得するか、あるいは全ての専攻を取得するか？
            # 通常、学生はmajor_idを持っているはず。
            # major_idがNULLのレコードは共通授業。
            
            sql = """
                SELECT 
                    t.id,
                    t.date,
                    t.period,
                    s.name as subject_name,
                    u.full_name as teacher_name,
                    t.major_id,
                    l.start_time,
                    l.end_time,
                    a.status as attendance_status
                FROM timetables t
                LEFT JOIN subjects s ON t.subject_id = s.id
                LEFT JOIN teacher_users u ON t.teacher_id = u.user_id
                LEFT JOIN lessontime l ON t.period = l.id
                LEFT JOIN attendance a ON t.id = a.timetable_id AND a.user_id = %s
                WHERE t.class_id = %s
                AND t.date BETWEEN %s AND %s
                AND (t.major_id = %s OR t.major_id IS NULL)
                ORDER BY t.date, t.period
            """
            
            cursor.execute(sql, (user_id, class_id, start_date, end_date, major_id))
            results = cursor.fetchall()
            
            # datetime/date/time objects need to be serializable if returned directly, 
            # but usually the route handler handles json conversion.
            # However, pymysql returns date/time objects.
            
            return results

    except Exception as e:
        print(f"get_timetable error: {e}")
        return []
    finally:
        conn.close()

def get_timetable_by_id(timetable_id):
    """
    指定された時間割IDの詳細（日付、開始時間など）を取得する
    """
    conn = db_connect()
    if not conn:
        return None

    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT 
                    t.id,
                    t.date,
                    l.start_time
                FROM timetables t
                LEFT JOIN lessontime l ON t.period = l.id
                WHERE t.id = %s
            """
            cursor.execute(sql, (timetable_id,))
            return cursor.fetchone()

    except Exception as e:
        print(f"get_timetable_by_id error: {e}")
        return None
    finally:
        if conn:
            conn.close()

