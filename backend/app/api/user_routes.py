from flask import Flask, request, jsonify,Blueprint
from google.oauth2 import id_token
from google.auth.transport import requests as grequests

from app.utility.auth.jwt import create_access_token, decode_access_token
from app.core.config import Config
import datetime
from app.utility.db.db_test import get_departments
import app.utility.db.db_user as db_user
import app.utility.db.db_class as db_class

user_bp = Blueprint('user', __name__)

@user_bp.route("/auth/google", methods=["POST"])
def google_login():
    """
    googleログイン認証を行い、データベースへの登録とJWTの発行を行う。

    """
    data = request.get_json()
    token = data.get("token")
    GOOGLE_CLIENT_ID = Config.GOOGLE_CLIENT_ID
    try:
        # IDトークンをGoogleで検証
        idinfo = id_token.verify_oauth2_token(token, grequests.Request(),audience=GOOGLE_CLIENT_ID)

        user = {
            "email": idinfo["email"],
            "name": idinfo["name"],
            "sub": idinfo["sub"]
        }

        email = user["email"]
        name = user["name"]
        google_sub = user["sub"]

        #ここからDB登録処理
        hasStudentUser = db_user.exists_student_user(google_sub)
        hasTeacherUser = db_user.exists_teacher_user(email,google_sub)
        
        if not hasStudentUser and not hasTeacherUser:
            user_id = email[0:8]
            admission_year_str = user_id[0:2]
            admission_year = int(admission_year_str) + 2000
            
            # Calculate Grade
            today = datetime.date.today()
            current_year = today.year
            if today.month < 4:
                current_year -= 1
            
            grade = current_year - admission_year + 1
            if grade < 1: grade = 1

            class_id = db_class.get_class_data(user_id[2:5], grade)
            
            result = db_user.regist_student_user(user_id,email,google_sub,admission_year,name,class_id)
            
            if not result:
                # DB登録失敗時は400を返す
                return jsonify({"error": "ユーザーデータ登録処理に失敗しました。"}), 400
        
        user["isTeacher"] = hasTeacherUser

        # JWT発行 (例: 有効期限1日)
        access_token = create_access_token(
            data={"sub": google_sub, "email": email, "name": name,"isTeacher":hasTeacherUser},
            expires_delta=datetime.timedelta(days=1)
        )

        # トークンを含めてレスポンスを返す
        return jsonify({"user": user, "access_token": access_token}), 200

    except Exception as e:
        print(f"ERROR in google_login: {e}", flush=True)
        return jsonify({"error": str(e)}), 400
    
@user_bp.route("/get/db_test", methods=["POST"])
def db_test():
    """
    データベーステスト用
    """
    rows = get_departments()

    return jsonify({"departments": rows}), 200

@user_bp.route("/me", methods=["GET"])
def get_me():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized"}), 401
    
    token = auth_header.split(" ")[1]
    payload = decode_access_token(token)
    if not payload:
        return jsonify({"error": "Invalid token"}), 401
    
    google_sub = payload.get("sub")
    
    # Get student info
    student_info = db_user.get_student_info(google_sub)
    if not student_info:
        return jsonify({"user_id": None, "error": "User not found"}), 404
        
    # Check for major selection need
    needs_major_selection = False
    available_majors = []
    
    if student_info.get("major_id") is None:
        majors = db_user.get_available_majors(student_info.get("department_id"))
        if majors:
            needs_major_selection = True
            available_majors = majors
            
    response = {
        "user_id": student_info.get("user_id"),
        "class_id": student_info.get("class_id"),
        "major_id": student_info.get("major_id"),
        "department_id": student_info.get("department_id"),
        "name": payload.get("name"),
        "email": payload.get("email"),
        "needs_major_selection": needs_major_selection,
        "available_majors": available_majors
    }
    
    return jsonify(response), 200

@user_bp.route("/me/major", methods=["PUT"])
def update_major():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized"}), 401
    
    token = auth_header.split(" ")[1]
    payload = decode_access_token(token)
    if not payload:
        return jsonify({"error": "Invalid token"}), 401
        
    google_sub = payload.get("sub")
    student_info = db_user.get_student_info(google_sub)
    
    if not student_info:
        return jsonify({"error": "User not found"}), 404
        
    user_id = student_info['user_id']
    
    data = request.get_json()
    major_id = data.get("major_id")
    
    if not major_id:
        return jsonify({"error": "major_id is required"}), 400
        
    success = db_user.update_student_major(user_id, major_id)
    if success:
        return jsonify({"message": "Major updated successfully"}), 200
    else:
        return jsonify({"error": "Failed to update major"}), 500
