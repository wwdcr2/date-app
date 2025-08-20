"""캘린더 및 일정 관련 라우트"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from calendar import monthrange
from app.extensions import db
from app.models.event import Event

# 블루프린트 생성
calendar_bp = Blueprint('calendar', __name__, url_prefix='/calendar')

@calendar_bp.route('/')
@login_required
def index():
    """캘린더 메인 페이지"""
    # 커플 연결 확인
    connection = current_user.get_couple_connection()
    if not connection:
        flash('파트너와 연결된 후 캘린더 기능을 사용할 수 있습니다.', 'warning')
        return redirect(url_for('couple.connect'))
    
    # 현재 날짜 정보
    today = date.today()
    year = request.args.get('year', today.year, type=int)
    month = request.args.get('month', today.month, type=int)
    
    return render_template('calendar/index.html', 
                         year=year, 
                         month=month, 
                         today=today)

@calendar_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """일정 등록"""
    # 커플 연결 확인
    connection = current_user.get_couple_connection()
    if not connection:
        flash('파트너와 연결된 후 일정을 등록할 수 있습니다.', 'warning')
        return redirect(url_for('couple.connect'))
    
    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            start_date = request.form.get('start_date', '').strip()
            start_time = request.form.get('start_time', '').strip()
            end_date = request.form.get('end_date', '').strip()
            end_time = request.form.get('end_time', '').strip()
            participant_type = request.form.get('participant_type', 'both')
            
            # 입력 검증
            if not title:
                flash('제목을 입력해주세요.', 'error')
                return render_template('calendar/create.html')
            
            if not start_date:
                flash('시작 날짜를 선택해주세요.', 'error')
                return render_template('calendar/create.html')
            
            # 날짜/시간 파싱
            try:
                start_datetime_str = f"{start_date} {start_time or '00:00'}"
                start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M')
                
                if end_date:
                    end_datetime_str = f"{end_date} {end_time or '23:59'}"
                    end_datetime = datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M')
                else:
                    # 종료 날짜가 없으면 시작 날짜와 같은 날로 설정
                    if end_time:
                        end_datetime_str = f"{start_date} {end_time}"
                        end_datetime = datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M')
                    else:
                        end_datetime = start_datetime + timedelta(hours=1)
                        
            except ValueError:
                flash('올바른 날짜/시간 형식을 입력해주세요.', 'error')
                return render_template('calendar/create.html')
            
            # 시작 시간이 종료 시간보다 늦은지 확인
            if start_datetime >= end_datetime:
                flash('종료 시간은 시작 시간보다 늦어야 합니다.', 'error')
                return render_template('calendar/create.html')
            
            # 일정 생성
            event = Event(
                couple_id=connection.id,
                title=title,
                description=description,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                participant_type=participant_type,
                created_by=current_user.id
            )
            
            db.session.add(event)
            db.session.commit()
            
            flash('일정이 등록되었습니다.', 'success')
            return redirect(url_for('calendar.index'))
            
        except Exception as e:
            db.session.rollback()
            flash('일정 등록 중 오류가 발생했습니다.', 'error')
            return render_template('calendar/create.html')
    
    # GET 요청 시 날짜 파라미터 처리
    selected_date = request.args.get('date')
    return render_template('calendar/create.html', selected_date=selected_date)

@calendar_bp.route('/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(event_id):
    """일정 수정"""
    # 커플 연결 확인
    connection = current_user.get_couple_connection()
    if not connection:
        flash('파트너와 연결된 후 일정을 수정할 수 있습니다.', 'warning')
        return redirect(url_for('couple.connect'))
    
    # 일정 조회
    event = Event.query.filter_by(id=event_id, couple_id=connection.id).first()
    if not event:
        flash('일정을 찾을 수 없습니다.', 'error')
        return redirect(url_for('calendar.index'))
    
    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            start_date = request.form.get('start_date', '').strip()
            start_time = request.form.get('start_time', '').strip()
            end_date = request.form.get('end_date', '').strip()
            end_time = request.form.get('end_time', '').strip()
            participant_type = request.form.get('participant_type', 'both')
            
            # 입력 검증
            if not title:
                flash('제목을 입력해주세요.', 'error')
                return render_template('calendar/edit.html', event=event)
            
            if not start_date:
                flash('시작 날짜를 선택해주세요.', 'error')
                return render_template('calendar/edit.html', event=event)
            
            # 날짜/시간 파싱
            try:
                start_datetime_str = f"{start_date} {start_time or '00:00'}"
                start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M')
                
                if end_date:
                    end_datetime_str = f"{end_date} {end_time or '23:59'}"
                    end_datetime = datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M')
                else:
                    if end_time:
                        end_datetime_str = f"{start_date} {end_time}"
                        end_datetime = datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M')
                    else:
                        end_datetime = start_datetime + timedelta(hours=1)
                        
            except ValueError:
                flash('올바른 날짜/시간 형식을 입력해주세요.', 'error')
                return render_template('calendar/edit.html', event=event)
            
            # 시작 시간이 종료 시간보다 늦은지 확인
            if start_datetime >= end_datetime:
                flash('종료 시간은 시작 시간보다 늦어야 합니다.', 'error')
                return render_template('calendar/edit.html', event=event)
            
            # 일정 수정
            event.title = title
            event.description = description
            event.start_datetime = start_datetime
            event.end_datetime = end_datetime
            event.participant_type = participant_type
            
            db.session.commit()
            
            flash('일정이 수정되었습니다.', 'success')
            return redirect(url_for('calendar.index'))
            
        except Exception as e:
            db.session.rollback()
            flash('일정 수정 중 오류가 발생했습니다.', 'error')
            return render_template('calendar/edit.html', event=event)
    
    return render_template('calendar/edit.html', event=event)

@calendar_bp.route('/<int:event_id>/delete', methods=['POST'])
@login_required
def delete(event_id):
    """일정 삭제"""
    # 커플 연결 확인
    connection = current_user.get_couple_connection()
    if not connection:
        return jsonify({'success': False, 'message': '권한이 없습니다.'})
    
    # 일정 조회
    event = Event.query.filter_by(id=event_id, couple_id=connection.id).first()
    if not event:
        return jsonify({'success': False, 'message': '일정을 찾을 수 없습니다.'})
    
    try:
        db.session.delete(event)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '일정이 삭제되었습니다.'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '일정 삭제 중 오류가 발생했습니다.'})

@calendar_bp.route('/api/events')
@login_required
def api_events():
    """캘린더 이벤트 API"""
    # 커플 연결 확인
    connection = current_user.get_couple_connection()
    if not connection:
        return jsonify({'success': False, 'message': '커플 연결이 필요합니다.'})
    
    # 날짜 범위 파라미터
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    
    if not year or not month:
        return jsonify({'success': False, 'message': '년도와 월을 지정해주세요.'})
    
    # 해당 월의 첫째 날과 마지막 날
    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])
    
    # 이벤트 조회
    events = Event.query.filter(
        Event.couple_id == connection.id,
        Event.start_datetime >= datetime.combine(first_day, datetime.min.time()),
        Event.start_datetime <= datetime.combine(last_day, datetime.max.time())
    ).order_by(Event.start_datetime.asc()).all()
    
    event_list = []
    for event in events:
        event_list.append({
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'start_datetime': event.start_datetime.isoformat(),
            'end_datetime': event.end_datetime.isoformat(),
            'start_date': event.start_datetime.date().isoformat(),
            'start_time': event.start_datetime.strftime('%H:%M'),
            'end_date': event.end_datetime.date().isoformat(),
            'end_time': event.end_datetime.strftime('%H:%M'),
            'participant_type': event.participant_type,
            'participant_text': event.get_participant_text(),
            'participant_color': event.get_participant_color(),
            'created_by': event.created_by,
            'created_at': event.created_at.isoformat()
        })
    
    return jsonify({'success': True, 'events': event_list})

@calendar_bp.route('/api/events/<date>')
@login_required
def api_events_by_date(date):
    """특정 날짜의 이벤트 조회 API"""
    # 커플 연결 확인
    connection = current_user.get_couple_connection()
    if not connection:
        return jsonify({'success': False, 'message': '커플 연결이 필요합니다.'})
    
    try:
        target_date = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'success': False, 'message': '올바른 날짜 형식이 아닙니다.'})
    
    # 해당 날짜의 이벤트 조회
    events = Event.query.filter(
        Event.couple_id == connection.id,
        Event.start_datetime >= datetime.combine(target_date, datetime.min.time()),
        Event.start_datetime < datetime.combine(target_date + timedelta(days=1), datetime.min.time())
    ).order_by(Event.start_datetime.asc()).all()
    
    event_list = []
    for event in events:
        event_list.append({
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'start_datetime': event.start_datetime.isoformat(),
            'end_datetime': event.end_datetime.isoformat(),
            'start_time': event.start_datetime.strftime('%H:%M'),
            'end_time': event.end_datetime.strftime('%H:%M'),
            'participant_type': event.participant_type,
            'participant_text': event.get_participant_text(),
            'participant_color': event.get_participant_color(),
            'created_by': event.created_by
        })
    
    return jsonify({'success': True, 'events': event_list, 'date': date})