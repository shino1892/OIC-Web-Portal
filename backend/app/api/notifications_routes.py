from flask import Blueprint, request, jsonify

from app.utility.auth.jwt import decode_access_token
from app.utility.db.db_user import get_student_info
from app.utility.db.db_notifications import list_notifications_for_student, mark_notification_read

notifications_bp = Blueprint('notifications', __name__)


def _get_student_context_from_request():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None, (jsonify({"error": "Authorization header missing"}), 401)

    token = auth_header.split(" ")[1] if len(auth_header.split(" ")) > 1 else None
    if not token:
        return None, (jsonify({"error": "Token missing"}), 401)

    payload = decode_access_token(token)
    if not payload:
        return None, (jsonify({"error": "Invalid or expired token"}), 401)

    google_sub = payload.get("sub")
    if not google_sub:
        return None, (jsonify({"error": "Invalid token payload"}), 401)

    student_info = get_student_info(google_sub)
    if not student_info:
        return None, (jsonify({"error": "User not found or not a student"}), 401)

    return student_info, None


@notifications_bp.route("/", methods=["GET"])
def get_notifications():
    student_info, err = _get_student_context_from_request()
    if err:
        return err

    user_id = student_info["user_id"]
    class_id = student_info.get("class_id")
    major_id = student_info.get("major_id")
    department_id = student_info.get("department_id")

    try:
        limit = int(request.args.get("limit", "100"))
    except ValueError:
        limit = 100

    rows = list_notifications_for_student(user_id, department_id, class_id, major_id, limit=limit)

    formatted = []
    for r in rows:
        formatted.append({
            "id": r["id"],
            "type": r["type"],
            "message": r["message"],
            "scope": r["scope"],
            "is_read": bool(r.get("is_read")),
            "read_at": r["read_at"].strftime('%Y-%m-%d %H:%M:%S') if r.get("read_at") else None,
            "created_at": r["created_at"].strftime('%Y-%m-%d %H:%M:%S') if r.get("created_at") else None,
        })

    return jsonify(formatted)


@notifications_bp.route("/read", methods=["POST"])
def read_notification():
    student_info, err = _get_student_context_from_request()
    if err:
        return err

    body = request.get_json(silent=True) or {}
    notification_id = body.get("notification_id")

    try:
        notification_id = int(notification_id)
    except Exception:
        return jsonify({"error": "notification_id is required"}), 400

    ok = mark_notification_read(student_info["user_id"], notification_id)
    if not ok:
        return jsonify({"error": "Failed to update"}), 500

    return jsonify({"ok": True})
