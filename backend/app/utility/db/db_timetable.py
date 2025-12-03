from app.utility.db.db_connect import db_connect

def get_timetable(class_id, major_id, start_date, end_date):
    """
    指定されたクラス、専攻、期間の時間割を取得する。
    major_idが指定されている場合は、その専攻の授業 + 共通授業(major_id IS NULL)を取得する。
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
                    l.end_time
                FROM timetables t
                LEFT JOIN subjects s ON t.subject_id = s.id
                LEFT JOIN teacher_users u ON t.teacher_id = u.user_id
                LEFT JOIN lessontime l ON t.period = l.id
                WHERE t.class_id = %s
                AND t.date BETWEEN %s AND %s
                AND (t.major_id = %s OR t.major_id IS NULL)
                ORDER BY t.date, t.period
            """
            
            cursor.execute(sql, (class_id, start_date, end_date, major_id))
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
