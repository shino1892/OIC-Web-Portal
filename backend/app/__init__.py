from flask import Flask
from flask_cors import CORS
from app.api.user_routes import user_bp
from app.api.timetable_routes import timeTable_bp
from app.core.config import Config


def create_app():
    app = Flask(__name__)
    
    # 設定を読み込む
    app.config.from_object(Config)

    # --- ① CORSをグローバルで先に適用 ---
    # 全エンドポイントでCORSを許可（特にlocalhost環境）
    CORS(
        app,
        origins=["http://localhost","http://localhost:3000", "http://127.0.0.1:3000"],
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "OPTIONS"]
    )

    # CORS(app, resources={r"*": {"origins": "*"}})  # 全許可

    # --- ② Blueprint登録 ---
    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(timeTable_bp, url_prefix="/api/timetables")

    # AIエンドポイント（フロントからは http://localhost:5000/generate を使う想定）
    from app.api.ai_routes import ai_bp
    app.register_blueprint(ai_bp)  # ルートは /generate    

    return app



