from flask import request, jsonify,Blueprint

import datetime
import app.utility.db.db_user as db_user
import app.utility.db.db_entry as db_entry
import app.utility.db.db_attendance as db_attendance
import app.utility.db.db_timetable as db_timetable

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/attend', methods=['POST'])
def attend():
    data = request.get_json()
    if not data or 'user_id' not in data or 'timetable_id' not in data:
        return jsonify({'message': 'User ID and Timetable ID are required'}), 400
    
    user_id = data['user_id']
    timetable_id = data['timetable_id']
    
    # 1. Get registered cards
    cards = db_user.get_user_cards(user_id)
    if not cards:
        return jsonify({'message': 'No cards registered for this user'}), 400
        
    # 2. Check entry logs
    entry_time = None
    for card in cards:
        idm = card['felica_idm']
        entry_time = db_entry.check_recent_entry(idm)
        if entry_time:
            break
            
    if not entry_time:
        return jsonify({'message': 'No recent entry record found'}), 403
        
    # 3. Determine Status
    status = '出席'
    timetable = db_timetable.get_timetable_by_id(timetable_id)
    
    if timetable:
        try:
            # Calculate class start datetime
            class_date = timetable['date'] # date object
            start_time_delta = timetable['start_time'] # timedelta object
            
            # Convert timedelta to time if needed, or just add to datetime
            class_start_dt = datetime.datetime.combine(class_date, datetime.time(0, 0)) + start_time_delta
            
            # Thresholds
            # Late: > 1 minute after start
            # Absent: > 15 minutes after start
            late_limit = class_start_dt + datetime.timedelta(minutes=1)
            absent_limit = class_start_dt + datetime.timedelta(minutes=15)
            
            # Assuming DB is UTC and Timetable is JST (Japan Standard Time)
            # We need to convert entry_time (UTC) to JST for comparison
            entry_time_jst = entry_time + datetime.timedelta(hours=9)
            
            if entry_time_jst > absent_limit:
                status = '欠席'
            elif entry_time_jst > late_limit:
                status = '遅刻'
            else:
                status = '出席'
                
        except Exception as e:
            print(f"Error calculating status: {e}")
            # Fallback to '出席'
            
    # 4. Register attendance
    if db_attendance.register_attendance(user_id, timetable_id, status):
        return jsonify({'message': 'Attendance registered successfully', 'status': status}), 200
    else:
        return jsonify({'message': 'Failed to register attendance'}), 500

@attendance_bp.route('/status', methods=['POST'])
def update_status():
    data = request.get_json()
    if not data or 'user_id' not in data or 'timetable_id' not in data or 'status' not in data:
        return jsonify({'message': 'User ID, Timetable ID, and Status are required'}), 400
        
    user_id = data['user_id']
    timetable_id = data['timetable_id']
    status = data['status']
    reason = data.get('reason')
    
    allowed_statuses = ['出席', '欠席', '遅刻', '早退', '公欠']
    if status not in allowed_statuses:
        return jsonify({'message': 'Invalid status'}), 400
        
    if db_attendance.update_attendance_status(user_id, timetable_id, status, reason):
        return jsonify({'message': 'Status updated successfully'}), 200
    else:
        return jsonify({'message': 'Failed to update status'}), 500

@attendance_bp.route('/entry', methods=['POST'])
def record_entry():
    data = request.get_json()
    if not data or 'idm' not in data:
        return jsonify({'message': 'IDm is required'}), 400
    
    idm = data['idm']
    if db_entry.add_entry_log(idm):
        return jsonify({'message': 'Entry recorded successfully'}), 200
    else:
        return jsonify({'message': 'Failed to record entry'}), 500

@attendance_bp.route('/register_card', methods=['POST'])
def register_card():
    data = request.get_json()
    if not data or 'idm' not in data or 'student_id' not in data:
        return jsonify({'message': 'IDm and Student ID are required'}), 400
    
    idm = data['idm']
    student_id = data['student_id']
    
    result = db_user.register_user_card(student_id, idm)
    
    if result == "SUCCESS":
        return jsonify({'message': 'Card registered successfully'}), 200
    elif result == "DUPLICATE":
        return jsonify({'message': 'Card IDm is already registered'}), 409
    else:
        return jsonify({'message': 'Failed to register card'}), 500

@attendance_bp.route('/summary', methods=['GET'])
def get_summary():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'message': 'User ID is required'}), 400
        
    summary = db_attendance.get_attendance_summary(user_id)
    if summary is not None:
        # Calculate Attendance Rate
        # Rate = (Attendance Count) / (Total - Public Absent) * 100
        # Attendance Count = Present + Late + Early = (Total - Public Absent) - Absent
        total = summary['total']
        absent = summary['欠席']
        public_absent = summary['公欠']
        
        denom = total - public_absent
        rate = 0
        
        if denom > 0:
            rate = (denom - absent) / denom * 100
        elif total > 0:
            # If all classes are Public Absence, treat as 100% attendance (no unauthorized absence)
            rate = 100.0
            
        summary['attendance_rate'] = round(rate, 1)

        # Get Subject Summary
        subject_summary = db_attendance.get_subject_attendance_summary(user_id)
        summary['subject_summary'] = subject_summary

        # Get Recent History
        recent_history = db_attendance.get_recent_attendance_history(user_id)
        summary['recent_history'] = recent_history

        return jsonify(summary), 200
    else:
        return jsonify({'message': 'Failed to get summary'}), 500
