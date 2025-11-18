import pymysql
import os
from app.core.config import Config

# 接続
def db_connect():
    conn = pymysql.connect(
        host=Config.DATABASE_HOST,
        user=Config.DATABASE_USER,
        password=Config.DATABASE_PASSWORD,
        database=Config.DATABASE_NAME,
        charset="utf8mb4",
        use_unicode=True,
        cursorclass=pymysql.cursors.DictCursor  # ← dictで返す
    )

    try:
        with conn.cursor() as cursor:
            cursor.execute("SET NAMES utf8mb4")   # ←これを追加！必須
            cursor.execute("SET character_set_connection=utf8mb4;")
            cursor.execute("SET character_set_results=utf8mb4;")
            cursor.execute("SET character_set_client=utf8mb4;")
            sql = "SELECT * FROM departments"
            cursor.execute(sql)
            rows = cursor.fetchall()
            print(rows)
            return rows

    finally:
        conn.close()
