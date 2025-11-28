from flask import Flask, request, jsonify
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
from flask import Blueprint, jsonify
from app.utility.db.db_test import get_departments
import app.utility.db.db_user as db_user
import app.utility.db.db_class as db_class

user_bp = Blueprint('user', __name__)

@user_bp.route("/auth/google", methods=["POST"])
def google_login():
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
            user_id = user["email"][0:7]
            admission_year = user_id[0:1]
            class_id = db_class.get_class_data(user_id[2:4])

            result = db_user.regist_student_user(user_id,user["email"],user["sub"],admission_year,user["name"],class_id)
            
            if not result:
                return jsonify({"error": "ユーザーデータ登録処理に失敗しました。"}), 400

        # ここでJWT発行を行う
        return jsonify({"user": user}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@user_bp.route("/regist/studentUser",methods=["POST"])
def has_student_user():
    try:
        

        result = db_user.regist_student_user()
        return jsonify({"hasUser": hasUser}),200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@user_bp.route("/get/db_test", methods=["POST"])
def db_test():
    rows = get_departments()

    return jsonify({"departments": rows}), 200
