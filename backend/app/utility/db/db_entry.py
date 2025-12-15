from app.utility.db.db_connect import db_connect

def add_entry_log(felica_idm):
    """
    入構ログをDBに保存する
    1日1回のみ記録する
    """
    conn = None
    try:
        conn = db_connect()
        if not conn:
            return False
            
        # 今日の記録が既にあるか確認
        check_sql = "SELECT COUNT(*) as count FROM entry_logs WHERE felica_idm = %s AND DATE(entered_at) = CURDATE()"
        
        with conn.cursor() as cursor:
            cursor.execute(check_sql, (felica_idm,))
            result = cursor.fetchone()
            if result and result['count'] > 0:
                # 既に記録済み
                return True

        sql = "INSERT INTO entry_logs (felica_idm) VALUES (%s)"
        
        with conn.cursor() as cursor:
            cursor.execute(sql, (felica_idm,))
            conn.commit()
            
        return True
        
    except Exception as e:
        print(f"add_entry_log エラー: {e}", flush=True)
        return False

    finally:
        if conn:
            conn.close()

def check_recent_entry(felica_idm, minutes=30):
    """
    指定されたIDmの入構記録が、現在時刻から指定分以内にあるか確認する
    """
    conn = None
    try:
        conn = db_connect()
        if not conn:
            return False
            
        # 現在時刻から minutes 分前以降のログがあるか
        sql = """
            SELECT entered_at 
            FROM entry_logs 
            WHERE felica_idm = %s 
            AND entered_at >= NOW() - INTERVAL %s MINUTE
            ORDER BY entered_at DESC
            LIMIT 1
        """
        
        with conn.cursor() as cursor:
            cursor.execute(sql, (felica_idm, minutes))
            result = cursor.fetchone()
            
            if result:
                return result['entered_at']
            return None
            
    except Exception as e:
        print(f"check_recent_entry エラー: {e}", flush=True)
        return None

    finally:
        if conn:
            conn.close()
