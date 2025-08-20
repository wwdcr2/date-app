"""D-Day 관련 라우트"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, date
from app.extensions import db
from app.models.dday import DDay

# 블루프린트 생성
dday_bp = Blueprint('dday', __name__, url_prefix='/dday')

@dday_bp.route('/')
@login_required
def index():
    """D-Day 목록 페이지"""
    # 커플 연결 확인
    connection = current_user.get_couple_connection()
    if not connection:
        flash('파트너와 연결된 후 D-Day 기능을 사용할 수 있습니다.', 'warning')
        return redirect(url_for('couple.connect'))
    
    # D-Day 목록 조회
    ddays = DDay.query.filter_by(couple_id=connection.id)\
                     .order_by(DDay.target_date.asc()).all()
    
    return render_template('dday/index.html', ddays=ddays)

@dday_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """D-Day 등록"""
    # 커플 연결 확인
    connection = current_user.get_couple_connection()
    if not connection:
        flash('파트너와 연결된 후 D-Day를 등록할 수 있습니다.', 'warning')
        return redirect(url_for('couple.connect'))
    
    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            target_date_str = request.form.get('target_date', '').strip()
            description = request.form.get('description', '').strip()
            
            # 입력 검증
            if not title:
                flash('제목을 입력해주세요.', 'error')
                return render_template('dday/create.html')
            
            if not target_date_str:
                flash('날짜를 선택해주세요.', 'error')
                return render_template('dday/create.html')
            
            # 날짜 파싱
            try:
                target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('올바른 날짜 형식을 입력해주세요.', 'error')
                return render_template('dday/create.html')
            
            # D-Day 생성
            dday = DDay(
                couple_id=connection.id,
                title=title,
                target_date=target_date,
                description=description,
                created_by=current_user.id
            )
            
            db.session.add(dday)
            db.session.commit()
            
            flash('D-Day가 등록되었습니다.', 'success')
            return redirect(url_for('dday.index'))
            
        except Exception as e:
            db.session.rollback()
            flash('D-Day 등록 중 오류가 발생했습니다.', 'error')
            return render_template('dday/create.html')
    
    return render_template('dday/create.html')

@dday_bp.route('/<int:dday_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(dday_id):
    """D-Day 수정"""
    # 커플 연결 확인
    connection = current_user.get_couple_connection()
    if not connection:
        flash('파트너와 연결된 후 D-Day를 수정할 수 있습니다.', 'warning')
        return redirect(url_for('couple.connect'))
    
    # D-Day 조회
    dday = DDay.query.filter_by(id=dday_id, couple_id=connection.id).first()
    if not dday:
        flash('D-Day를 찾을 수 없습니다.', 'error')
        return redirect(url_for('dday.index'))
    
    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            target_date_str = request.form.get('target_date', '').strip()
            description = request.form.get('description', '').strip()
            
            # 입력 검증
            if not title:
                flash('제목을 입력해주세요.', 'error')
                return render_template('dday/edit.html', dday=dday)
            
            if not target_date_str:
                flash('날짜를 선택해주세요.', 'error')
                return render_template('dday/edit.html', dday=dday)
            
            # 날짜 파싱
            try:
                target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('올바른 날짜 형식을 입력해주세요.', 'error')
                return render_template('dday/edit.html', dday=dday)
            
            # D-Day 수정
            dday.title = title
            dday.target_date = target_date
            dday.description = description
            
            db.session.commit()
            
            flash('D-Day가 수정되었습니다.', 'success')
            return redirect(url_for('dday.index'))
            
        except Exception as e:
            db.session.rollback()
            flash('D-Day 수정 중 오류가 발생했습니다.', 'error')
            return render_template('dday/edit.html', dday=dday)
    
    return render_template('dday/edit.html', dday=dday)

@dday_bp.route('/<int:dday_id>/delete', methods=['POST'])
@login_required
def delete(dday_id):
    """D-Day 삭제"""
    # 커플 연결 확인
    connection = current_user.get_couple_connection()
    if not connection:
        return jsonify({'success': False, 'message': '권한이 없습니다.'})
    
    # D-Day 조회
    dday = DDay.query.filter_by(id=dday_id, couple_id=connection.id).first()
    if not dday:
        return jsonify({'success': False, 'message': 'D-Day를 찾을 수 없습니다.'})
    
    try:
        db.session.delete(dday)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'D-Day가 삭제되었습니다.'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'D-Day 삭제 중 오류가 발생했습니다.'})

@dday_bp.route('/api/list')
@login_required
def api_list():
    """D-Day 목록 API"""
    # 커플 연결 확인
    connection = current_user.get_couple_connection()
    if not connection:
        return jsonify({'success': False, 'message': '커플 연결이 필요합니다.'})
    
    # D-Day 목록 조회
    ddays = DDay.query.filter_by(couple_id=connection.id)\
                     .order_by(DDay.target_date.asc()).all()
    
    dday_list = []
    for dday in ddays:
        dday_list.append({
            'id': dday.id,
            'title': dday.title,
            'target_date': dday.target_date.isoformat(),
            'description': dday.description,
            'days_remaining': dday.days_remaining(),
            'status_text': dday.get_status_text(),
            'is_past': dday.is_past(),
            'created_by': dday.created_by,
            'created_at': dday.created_at.isoformat()
        })
    
    return jsonify({'success': True, 'ddays': dday_list})