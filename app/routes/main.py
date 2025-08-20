"""메인 페이지 라우트"""

import os
from flask import Blueprint, render_template, request, jsonify, send_from_directory, current_app, abort
from flask_login import login_required, current_user
from app.extensions import db
from datetime import datetime

# 블루프린트 생성
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """메인 페이지"""
    if current_user.is_authenticated:
        # 로그인된 사용자는 대시보드로
        return render_template('main/dashboard.html')
    else:
        # 비로그인 사용자는 랜딩 페이지로
        return render_template('main/landing.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """대시보드 페이지"""
    partner = current_user.get_partner()
    is_connected = current_user.is_connected_to_partner()
    
    return render_template('main/dashboard.html', 
                         user=current_user,
                         partner=partner,
                         is_connected=is_connected)

@main_bp.route('/about')
def about():
    """소개 페이지"""
    return render_template('main/about.html')

@main_bp.route('/api/dashboard-data')
@login_required
def dashboard_data():
    """대시보드 데이터 API"""
    from app.models.dday import DDay
    from app.models.event import Event
    from app.models.mood import MoodEntry
    from app.models.notification import Notification
    from datetime import date, datetime, timedelta
    
    # 커플 연결 정보
    connection = current_user.get_couple_connection()
    partner = current_user.get_partner()
    
    data = {
        'user': {
            'id': current_user.id,
            'name': current_user.name,
            'email': current_user.email
        },
        'partner': {
            'id': partner.id,
            'name': partner.name,
            'email': partner.email
        } if partner else None,
        'is_connected': connection is not None
    }
    
    if connection:
        # D-Day 정보 (최근 3개)
        ddays = DDay.query.filter_by(couple_id=connection.id)\
                         .order_by(DDay.target_date.asc())\
                         .limit(3).all()
        
        data['ddays'] = [{
            'id': dday.id,
            'title': dday.title,
            'target_date': dday.target_date.isoformat(),
            'days_remaining': dday.days_remaining(),
            'status_text': dday.get_status_text(),
            'is_past': dday.is_past()
        } for dday in ddays]
        
        # 오늘의 이벤트
        today = date.today()
        today_events = Event.query.filter_by(couple_id=connection.id)\
                                 .filter(Event.start_datetime >= datetime.combine(today, datetime.min.time()))\
                                 .filter(Event.start_datetime < datetime.combine(today + timedelta(days=1), datetime.min.time()))\
                                 .order_by(Event.start_datetime.asc()).all()
        
        data['today_events'] = [{
            'id': event.id,
            'title': event.title,
            'start_time': event.start_datetime.strftime('%H:%M'),
            'participant_type': event.participant_type,
            'participant_text': event.get_participant_text(),
            'participant_color': event.get_participant_color()
        } for event in today_events]
        
        # 오늘의 기분 (파트너 포함)
        today_moods = MoodEntry.query.filter(
            MoodEntry.date == today,
            MoodEntry.user_id.in_([current_user.id, partner.id if partner else 0])
        ).all()
        
        data['today_moods'] = {
            'my_mood': None,
            'partner_mood': None
        }
        
        for mood in today_moods:
            mood_data = {
                'level': mood.mood_level,
                'emoji': mood.get_mood_emoji(),
                'text': mood.get_mood_text(),
                'note': mood.note
            }
            
            if mood.user_id == current_user.id:
                data['today_moods']['my_mood'] = mood_data
            elif partner and mood.user_id == partner.id:
                data['today_moods']['partner_mood'] = mood_data
    
    # 읽지 않은 알림 수
    unread_notifications = Notification.get_unread_count(current_user.id)
    data['unread_notifications'] = unread_notifications
    
    return jsonify(data)

@main_bp.route('/api/mood/record', methods=['POST'])
@login_required
def record_mood():
    """기분 기록 API"""
    from app.models.mood import MoodEntry
    from datetime import date
    
    try:
        data = request.get_json(force=True) or {}
        mood_level = data.get('mood_level')
        note = data.get('note', '')
        record_date = data.get('date')
        
        # 입력 검증
        if not mood_level or mood_level < 1 or mood_level > 5:
            return jsonify({'success': False, 'message': '기분 레벨은 1-5 사이여야 합니다.'})
        
        # 날짜 파싱
        try:
            if record_date:
                record_date = date.fromisoformat(record_date)
            else:
                record_date = date.today()
        except ValueError:
            record_date = date.today()
        
        # 기존 기분 기록 확인
        existing_mood = MoodEntry.query.filter_by(
            user_id=current_user.id,
            date=record_date
        ).first()
        
        if existing_mood:
            # 기존 기록 업데이트
            existing_mood.mood_level = mood_level
            existing_mood.note = note
            existing_mood.updated_at = datetime.utcnow()
            message = '기분이 수정되었습니다.'
        else:
            # 새 기록 생성
            new_mood = MoodEntry(
                user_id=current_user.id,
                mood_level=mood_level,
                note=note,
                date=record_date
            )
            db.session.add(new_mood)
            message = '기분이 기록되었습니다.'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': message
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'기분 기록 중 오류가 발생했습니다: {str(e)}'
        })

@main_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    """업로드된 파일 서빙"""
    upload_folder = current_app.config['UPLOAD_FOLDER']
    
    # 파일 존재 여부 확인
    file_path = os.path.join(upload_folder, filename)
    if not os.path.exists(file_path):
        abort(404)
    
    # 보안을 위해 파일명 검증
    if '..' in filename or filename.startswith('/'):
        abort(404)
    
    return send_from_directory(upload_folder, filename)