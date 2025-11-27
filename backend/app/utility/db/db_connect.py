import pymysql
from app.core.config import Config

# 接続
def db_connect():
    try:
        conn = pymysql.connect(
            host=Config.DATABASE_HOST,
            user=Config.DATABASE_USER,
            password=Config.DATABASE_PASSWORD,
            database=Config.DATABASE_NAME,
            charset="utf8mb4",
            use_unicode=True,
            cursorclass=pymysql.cursors.DictCursor  # ← dictで返す
        )

        return conn

    except:
        return
