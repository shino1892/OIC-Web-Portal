from flask import Blueprint, request, jsonify
from app.utility.db.db_timetable import get_timetable
from app.utility.db.db_user import get_student_info
from app.utility.db.db_class import get_majors_by_department
from app.utility.auth.jwt import decode_access_token
from app.core.config import Config
import datetime

timeTable_bp = Blueprint('timetable', __name__)

@timeTable_bp.route("/majors", methods=["GET"])
def get_majors():
    """
    ユーザーの学科に関連する専攻一覧を取得する
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Authorization header missing"}), 401
    
    token = auth_header.split(" ")[1] if len(auth_header.split(" ")) > 1 else None
    if not token:
        return jsonify({"error": "Token missing"}), 401

    payload = decode_access_token(token)
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
        
    google_sub = payload.get("sub")
    student_info = get_student_info(google_sub)
    
    if not student_info:
        return jsonify({"error": "User not found"}), 401
        
    department_id = student_info.get('department_id')
    if not department_id:
        return jsonify({"majors": []}), 200
        
    majors = get_majors_by_department(department_id)
    return jsonify({"majors": majors}), 200

@timeTable_bp.route("/", methods=["GET"])
def get_timetables():
    """
    時間割を取得するエンドポイント
    Query Params:
      start_date: YYYY-MM-DD
      end_date: YYYY-MM-DD
    Headers:
      Authorization: Bearer <token> (Custom JWT)
    """
    
    # 1. Auth Check
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Authorization header missing"}), 401
    
    token = auth_header.split(" ")[1] if len(auth_header.split(" ")) > 1 else None
    if not token:
        return jsonify({"error": "Token missing"}), 401

    # Verify Custom JWT
    payload = decode_access_token(token)
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
        
    google_sub = payload.get("sub")
    if not google_sub:
        return jsonify({"error": "Invalid token payload"}), 401

    # 2. Get User Info
    student_info = get_student_info(google_sub)
    if not student_info:
        return jsonify({"error": "User not found or not a student"}), 401
        
    class_id = student_info['class_id']
    # major_id = student_info['major_id'] # DBから取得したmajor_idはデフォルトとして使うが、クエリパラメータで上書き可能にする

    # 3. Parse Dates & Major
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    requested_major_id = request.args.get('major_id')

    # クエリパラメータでmajor_idが指定されていればそれを使用、なければDBの値を使用
    if requested_major_id:
        try:
            major_id = int(requested_major_id)
        except ValueError:
            major_id = student_info['major_id'] # 不正な値の場合はデフォルトに戻す
    else:
        major_id = student_info['major_id']
    
    if not start_date_str or not end_date_str:
        # Default to current week if not provided
        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=today.weekday())
        end_date = start_date + datetime.timedelta(days=6)
    else:
        try:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    # 4. Fetch Data
    user_id = student_info['user_id']
    timetable_data = get_timetable(class_id, major_id, start_date, end_date, user_id)
    
    # 5. Format Response
    formatted_data = []
    for entry in timetable_data:
        formatted_data.append({
            "id": entry['id'],
            "date": entry['date'].strftime('%Y-%m-%d'),
            "period": entry['period'],
            "subject_name": entry['subject_name'],
            "teacher_name": entry['teacher_name'],
            "major_id": entry['major_id'],
            "start_time": str(entry['start_time']) if entry['start_time'] else None,
            "end_time": str(entry['end_time']) if entry['end_time'] else None,
            "attendance_status": entry.get('attendance_status')
        })

    return jsonify(formatted_data)
