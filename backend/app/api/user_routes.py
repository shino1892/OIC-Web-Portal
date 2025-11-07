from flask import Flask, request, jsonify
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
from flask import Blueprint, jsonify
from flask_cors import CORS

user_bp = Blueprint('user', __name__)
CORS(user_bp, origins=["http://localhost:3000"], supports_credentials=True)

@user_bp.after_request
def add_cors_headers(response):
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    return response

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
            "picture": idinfo.get("picture")
        }

        # 必要であればここでJWT発行やDB登録を行う
        return jsonify({"user": user}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
