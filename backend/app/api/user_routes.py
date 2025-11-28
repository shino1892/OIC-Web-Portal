from flask import Flask, request, jsonify
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
from flask import Blueprint, jsonify
from app.utility.auth.jwt import create_access_token
import datetime
from app.utility.db.db_test import get_departments
import app.utility.db.db_user as db_user

user_bp = Blueprint('user', __name__)

@user_bp.route("/auth/google", methods=["POST"])
def google_login():
    """
    googleログイン認証を行い、データベースへの登録とJWTの発行を行う。

    """
    data = request.get_json()
    token = data.get("token")

    try:
        # IDトークンをGoogleで検証
        idinfo = id_token.verify_oauth2_token(token, grequests.Request())

        user = {
            "email": idinfo["email"],
            "name": idinfo["name"],
            "sub": idinfo["sub"]
        }

        #ここからDB登録処理
        hasUser = db_user.exists_student_user(user["sub"])

        if not hasUser:
            user_id = 0
            admission_year = 0
            class_id = 0

            result = db_user.regist_student_user(user_id,user["email"],user["sub"],admission_year,user["name"],class_id)
            
            if not result:
                return jsonify({"error": "ユーザーデータ登録処理に失敗しました。"}), 400

        # JWT発行 (例: 有効期限1日)
        access_token = create_access_token(
            data={"sub": user["sub"], "email": user["email"], "name": user["name"]},
            expires_delta=datetime.timedelta(days=1)
        )

        # トークンを含めてレスポンスを返す
        return jsonify({"user": user, "access_token": access_token}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@user_bp.route("/get/db_test", methods=["POST"])
def db_test():
    """
    データベーステスト用
    """
    rows = get_departments()

    return jsonify({"departments": rows}), 200
