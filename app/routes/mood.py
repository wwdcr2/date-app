"""무드 트래커 라우트"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from sqlalchemy import func, extract
from app.extensions import db
from app.models.mood import MoodEntry
import calendar

# 블루프린트 생성
mood_bp = Blueprint('mood', __name__, url_prefix='/mood')

@mood_bp.route('/')
@login_required
def index():
    """무드 트래커 메인 페이지"""
    # 커플 연결 확인
    connection = current_user.get_couple_connection()
    if not connection:
        flash('파트너와 연결된 후 무드 트래커를 사용할 수 있습니다.', 'warning')
        return redirect(url_for('couple.connect'))
    
    # 현재 월의 기분 데이터 가져오기
    today = date.today()
    start_of_month = date(today.year, today.month, 1)
    
    # 다음 달의 첫 날을 구해서 이번 달의 마지막 날 계산
    if today.month == 12:
        end_of_month = date(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        end_of_month = date(today.year, today.month + 1, 1) - timedelta(days=1)
    
    # 내 기분 데이터
    my_moods = MoodEntry.query.filter(
        MoodEntry.user_id == current_user.id,
        MoodEntry.date >= start_of_month,
        MoodEntry.date <= end_of_month
    ).all()
    
    # 파트너 기분 데이터
    partner = current_user.get_partner()
    partner_moods = []
    if partner:
        partner_moods = MoodEntry.query.filter(
            MoodEntry.user_id == partner.id,
            MoodEntry.date >= start_of_month,
            MoodEntry.date <= end_of_month
        ).all()
    
    # 오늘의 기분 확인
    today_mood = MoodEntry.query.filter_by(
        user_id=current_user.id,
        date=today
    ).first()
    
    return render_template('mood/index.html',
                         my_moods=my_moods,
                         partner_moods=partner_moods,
                         partner=partner,
                         today_mood=today_mood,
                         current_month=today.strftime('%Y-%m'),
                         month_name=today.strftime('%Y년 %m월'))

@mood_bp.route('/record', methods=['GET', 'POST'])
@login_required
def record():
    """기분 기록 페이지"""
    # 커플 연결 확인
    connection = current_user.get_couple_connection()
    if not connection:
        flash('파트너와 연결된 후 무드 트래커를 사용할 수 있습니다.', 'warning')
        return redirect(url_for('couple.connect'))
    
    if request.method == 'POST':
        try:
            mood_level = int(request.form.get('mood_level'))
            note = request.form.get('note', '').strip()
            record_date = request.form.get('date')
            
            # 입력 검증
            if mood_level < 1 or mood_level > 5:
                flash('기분 레벨은 1-5 사이여야 합니다.', 'error')
                return redirect(url_for('mood.record'))
            
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
                flash('기분이 수정되었습니다.', 'success')
            else:
                # 새 기록 생성
                new_mood = MoodEntry(
                    user_id=current_user.id,
                    mood_level=mood_level,
                    note=note,
                    date=record_date
                )
                db.session.add(new_mood)
                flash('기분이 기록되었습니다.', 'success')
            
            db.session.commit()
            
            # 실시간 알림 전송 (새로 기록한 경우에만)
            if not existing_mood:
                from app.socketio_events import notify_mood_update
                notify_mood_update(
                    current_user.id,
                    mood_level,
                    new_mood.get_mood_emoji(),
                    new_mood.get_mood_text()
                )
            
            return redirect(url_for('mood.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'기분 기록 중 오류가 발생했습니다: {str(e)}', 'error')
    
    # 오늘의 기분 확인
    today = date.today()
    today_mood = MoodEntry.query.filter_by(
        user_id=current_user.id,
        date=today
    ).first()
    
    return render_template('mood/record.html',
                         today_mood=today_mood,
                         today=today)

@mood_bp.route('/calendar')
@mood_bp.route('/calendar/<year_month>')
@login_required
def calendar_view(year_month=None):
    """무드 캘린더 뷰"""
    # 커플 연결 확인
    connection = current_user.get_couple_connection()
    if not connection:
        flash('파트너와 연결된 후 무드 트래커를 사용할 수 있습니다.', 'warning')
        return redirect(url_for('couple.connect'))
    
    # 년월 파싱
    if year_month:
        try:
            year, month = map(int, year_month.split('-'))
        except ValueError:
            year, month = date.today().year, date.today().month
    else:
        today = date.today()
        year, month = today.year, today.month
    
    # 해당 월의 첫 날과 마지막 날
    start_of_month = date(year, month, 1)
    if month == 12:
        end_of_month = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_of_month = date(year, month + 1, 1) - timedelta(days=1)
    
    # 내 기분 데이터
    my_moods = MoodEntry.query.filter(
        MoodEntry.user_id == current_user.id,
        MoodEntry.date >= start_of_month,
        MoodEntry.date <= end_of_month
    ).all()
    
    # 파트너 기분 데이터
    partner = current_user.get_partner()
    partner_moods = []
    if partner:
        partner_moods = MoodEntry.query.filter(
            MoodEntry.user_id == partner.id,
            MoodEntry.date >= start_of_month,
            MoodEntry.date <= end_of_month
        ).all()
    
    # 캘린더 데이터 구성
    cal = calendar.monthcalendar(year, month)
    
    # 기분 데이터를 날짜별로 매핑
    my_mood_map = {mood.date.day: mood for mood in my_moods}
    partner_mood_map = {mood.date.day: mood for mood in partner_moods}
    
    # 이전/다음 월 계산
    if month == 1:
        prev_month = f"{year-1}-12"
    else:
        prev_month = f"{year}-{month-1:02d}"
    
    if month == 12:
        next_month = f"{year+1}-01"
    else:
        next_month = f"{year}-{month+1:02d}"
    
    return render_template('mood/calendar.html',
                         calendar_data=cal,
                         my_mood_map=my_mood_map,
                         partner_mood_map=partner_mood_map,
                         partner=partner,
                         current_year=year,
                         current_month=month,
                         month_name=f"{year}년 {month}월",
                         prev_month=prev_month,
                         next_month=next_month,
                         today=date.today())

@mood_bp.route('/statistics')
@mood_bp.route('/statistics/<period>')
@login_required
def statistics(period='month'):
    """무드 통계 페이지"""
    # 커플 연결 확인
    connection = current_user.get_couple_connection()
    if not connection:
        flash('파트너와 연결된 후 무드 트래커를 사용할 수 있습니다.', 'warning')
        return redirect(url_for('couple.connect'))
    
    today = date.today()
    
    # 기간 설정
    if period == 'week':
        start_date = today - timedelta(days=7)
        period_name = '최근 7일'
    elif period == 'month':
        start_date = date(today.year, today.month, 1)
        period_name = f'{today.year}년 {today.month}월'
    elif period == 'year':
        start_date = date(today.year, 1, 1)
        period_name = f'{today.year}년'
    else:
        start_date = date(today.year, today.month, 1)
        period_name = f'{today.year}년 {today.month}월'
    
    # 내 통계
    my_stats = MoodEntry.get_mood_statistics(current_user.id, start_date, today)
    
    # 파트너 통계
    partner = current_user.get_partner()
    partner_stats = None
    if partner:
        partner_stats = MoodEntry.get_mood_statistics(partner.id, start_date, today)
    
    return render_template('mood/statistics.html',
                         my_stats=my_stats,
                         partner_stats=partner_stats,
                         partner=partner,
                         period=period,
                         period_name=period_name)

@mood_bp.route('/api/record', methods=['POST'])
@login_required
def api_record():
    """기분 기록 API"""
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
        
        # 실시간 알림 전송 (새로 기록한 경우에만)
        if not existing_mood:
            from app.socketio_events import notify_mood_update
            notify_mood_update(
                current_user.id,
                mood_level,
                new_mood.get_mood_emoji(),
                new_mood.get_mood_text()
            )
        
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

@mood_bp.route('/api/monthly-data/<year_month>')
@login_required
def api_monthly_data(year_month):
    """월별 기분 데이터 API"""
    try:
        year, month = map(int, year_month.split('-'))
    except ValueError:
        return jsonify({'success': False, 'message': '잘못된 날짜 형식입니다.'})
    
    # 해당 월의 첫 날과 마지막 날
    start_of_month = date(year, month, 1)
    if month == 12:
        end_of_month = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_of_month = date(year, month + 1, 1) - timedelta(days=1)
    
    # 내 기분 데이터
    my_moods = MoodEntry.query.filter(
        MoodEntry.user_id == current_user.id,
        MoodEntry.date >= start_of_month,
        MoodEntry.date <= end_of_month
    ).all()
    
    # 파트너 기분 데이터
    partner = current_user.get_partner()
    partner_moods = []
    if partner:
        partner_moods = MoodEntry.query.filter(
            MoodEntry.user_id == partner.id,
            MoodEntry.date >= start_of_month,
            MoodEntry.date <= end_of_month
        ).all()
    
    return jsonify({
        'success': True,
        'my_moods': [{
            'date': mood.date.isoformat(),
            'level': mood.mood_level,
            'emoji': mood.get_mood_emoji(),
            'text': mood.get_mood_text(),
            'color': mood.get_mood_color(),
            'note': mood.note
        } for mood in my_moods],
        'partner_moods': [{
            'date': mood.date.isoformat(),
            'level': mood.mood_level,
            'emoji': mood.get_mood_emoji(),
            'text': mood.get_mood_text(),
            'color': mood.get_mood_color(),
            'note': mood.note
        } for mood in partner_moods] if partner else [],
        'partner_name': partner.name if partner else None
    })