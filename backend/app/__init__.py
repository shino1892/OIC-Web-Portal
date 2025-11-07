from flask import Flask
from flask_cors import CORS
from app.api.routes import api_bp
from app.api.user_routes import user_bp
from app.core.config import Config


def create_app():
    app = Flask(__name__)
    
    # 設定を読み込む
    app.config.from_object(Config)

    # --- ① CORSをグローバルで先に適用 ---
    # 全エンドポイントでCORSを許可（特にlocalhost環境）
    CORS(
        app,
        origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "OPTIONS"]
    )

    # --- ② Blueprint登録 ---
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(user_bp, url_prefix="/api/users")

    return app
