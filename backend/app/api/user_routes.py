from flask import Flask, request, jsonify
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
from flask import Blueprint, jsonify
from app.utility.db.db_test import get_departments
import app.utility.db.db_user as db_user

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

        # 必要であればここでJWT発行やDB登録を行う
        return jsonify({"user": user}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@user_bp.route("/get/hasUser",methods=["POST"])
def has_student_user():
    try:
        hasUser = db_user.exists_student_user()
        return jsonify({"hasUser": hasUser}),200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@user_bp.route("/get/db_test", methods=["POST"])
def db_test():
    rows = get_departments()

    return jsonify({"departments": rows}), 200
