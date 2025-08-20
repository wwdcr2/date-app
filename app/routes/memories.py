"""메모리 북 관련 라우트"""

import os
from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models.memory import Memory
from app.models.couple import CoupleConnection
from app.utils.security import (
    couple_relationship_required, 
    validate_couple_access, 
    sanitize_input,
    FileUploadValidator,
    validate_form_data
)

memories_bp = Blueprint('memories', __name__, url_prefix='/memories')

@memories_bp.route('/')
@login_required
@couple_relationship_required
def index():
    """메모리 북 메인 페이지"""
    connection = current_user.get_couple_connection()
    
    # 페이지네이션을 위한 페이지 번호
    page = request.args.get('page', 1, type=int)
    per_page = 12  # 페이지당 메모리 수
    
    # 메모리 목록 조회 (최신순)
    memories = Memory.query.filter_by(couple_id=connection.id)\
                          .order_by(Memory.memory_date.desc(), Memory.created_at.desc())\
                          .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('memories/index.html', memories=memories)

@memories_bp.route('/add', methods=['GET', 'POST'])
@login_required
@couple_relationship_required
def add():
    """새 메모리 추가"""
    if request.method == 'POST':
        # 폼 데이터 검증 규칙
        validation_rules = {
            'title': {
                'required': True,
                'max_length': 100,
                'min_length': 1
            },
            'content': {
                'required': True,
                'max_length': 2000,
                'min_length': 1
            },
            'memory_date': {
                'required': True,
                'pattern': r'^\d{4}-\d{2}-\d{2}$',
                'pattern_message': '올바른 날짜 형식이 아닙니다. (YYYY-MM-DD)'
            }
        }
        
        # 입력 데이터 검증
        form_errors = validate_form_data(request.form, validation_rules)
        if form_errors:
            for field, errors in form_errors.items():
                for error in errors:
                    flash(error, 'error')
            return render_template('memories/add.html')
        
        # 입력 데이터 정제
        title = sanitize_input(request.form.get('title', '').strip(), max_length=100)
        content = sanitize_input(request.form.get('content', '').strip(), max_length=2000)
        memory_date_str = request.form.get('memory_date', '')
        
        try:
            memory_date = datetime.strptime(memory_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('올바른 날짜 형식이 아닙니다.', 'error')
            return render_template('memories/add.html')
        
        # 미래 날짜 체크
        if memory_date > date.today():
            flash('미래 날짜는 선택할 수 없습니다.', 'error')
            return render_template('memories/add.html')
        
        # 이미지 파일 처리 (보안 강화)
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                upload_folder = current_app.config['UPLOAD_FOLDER']
                filename, errors = FileUploadValidator.secure_save_file(file, upload_folder)
                
                if errors:
                    for error in errors:
                        flash(error, 'error')
                    return render_template('memories/add.html')
                
                image_filename = filename
        
        # 메모리 생성
        connection = current_user.get_couple_connection()
        memory = Memory(
            couple_id=connection.id,
            title=title,
            content=content,
            memory_date=memory_date,
            image_path=image_filename,
            created_by=current_user.id
        )
        
        try:
            db.session.add(memory)
            db.session.commit()
            
            # 실시간 알림 전송
            from app.socketio_events import notify_new_memory
            notify_new_memory(current_user.id, title)
            
            flash('추억이 성공적으로 저장되었습니다!', 'success')
            return redirect(url_for('memories.index'))
        except Exception as e:
            db.session.rollback()
            flash('추억 저장 중 오류가 발생했습니다.', 'error')
            current_app.logger.error(f"Memory creation error: {e}")
            return render_template('memories/add.html')
    
    return render_template('memories/add.html')

@memories_bp.route('/<int:memory_id>')
@login_required
@couple_relationship_required
def detail(memory_id):
    """메모리 상세 보기"""
    connection = current_user.get_couple_connection()
    memory = Memory.query.filter_by(id=memory_id, couple_id=connection.id).first_or_404()
    
    # 커플 관계 검증
    if not validate_couple_access(memory.couple_id):
        flash('접근 권한이 없습니다.', 'error')
        return redirect(url_for('memories.index'))
    
    return render_template('memories/detail.html', memory=memory)

@memories_bp.route('/<int:memory_id>/edit', methods=['GET', 'POST'])
@login_required
@couple_relationship_required
def edit(memory_id):
    """메모리 수정"""
    connection = current_user.get_couple_connection()
    memory = Memory.query.filter_by(id=memory_id, couple_id=connection.id).first_or_404()
    
    # 작성자만 수정 가능
    if memory.created_by != current_user.id:
        flash('자신이 작성한 추억만 수정할 수 있습니다.', 'error')
        return redirect(url_for('memories.detail', memory_id=memory_id))
    
    if request.method == 'POST':
        # 폼 데이터 검증 규칙
        validation_rules = {
            'title': {
                'required': True,
                'max_length': 100,
                'min_length': 1
            },
            'content': {
                'required': True,
                'max_length': 2000,
                'min_length': 1
            },
            'memory_date': {
                'required': True,
                'pattern': r'^\d{4}-\d{2}-\d{2}$',
                'pattern_message': '올바른 날짜 형식이 아닙니다. (YYYY-MM-DD)'
            }
        }
        
        # 입력 데이터 검증
        form_errors = validate_form_data(request.form, validation_rules)
        if form_errors:
            for field, errors in form_errors.items():
                for error in errors:
                    flash(error, 'error')
            return render_template('memories/edit.html', memory=memory)
        
        # 입력 데이터 정제
        title = sanitize_input(request.form.get('title', '').strip(), max_length=100)
        content = sanitize_input(request.form.get('content', '').strip(), max_length=2000)
        memory_date_str = request.form.get('memory_date', '')
        
        try:
            memory_date = datetime.strptime(memory_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('올바른 날짜 형식이 아닙니다.', 'error')
            return render_template('memories/edit.html', memory=memory)
        
        # 미래 날짜 체크
        if memory_date > date.today():
            flash('미래 날짜는 선택할 수 없습니다.', 'error')
            return render_template('memories/edit.html', memory=memory)
        
        # 이미지 파일 처리 (보안 강화)
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                upload_folder = current_app.config['UPLOAD_FOLDER']
                filename, errors = FileUploadValidator.secure_save_file(file, upload_folder)
                
                if errors:
                    for error in errors:
                        flash(error, 'error')
                    return render_template('memories/edit.html', memory=memory)
                
                # 기존 이미지 삭제
                memory.delete_image()
                memory.image_path = filename
        
        # 이미지 삭제 요청 처리
        if request.form.get('remove_image') == 'true':
            memory.delete_image()
            memory.image_path = None
        
        # 메모리 업데이트
        memory.title = title
        memory.content = content
        memory.memory_date = memory_date
        
        try:
            db.session.commit()
            flash('추억이 성공적으로 수정되었습니다!', 'success')
            return redirect(url_for('memories.detail', memory_id=memory_id))
        except Exception as e:
            db.session.rollback()
            flash('추억 수정 중 오류가 발생했습니다.', 'error')
            current_app.logger.error(f"Memory update error: {e}")
            return render_template('memories/edit.html', memory=memory)
    
    return render_template('memories/edit.html', memory=memory)

@memories_bp.route('/<int:memory_id>/delete', methods=['POST'])
@login_required
@couple_relationship_required
def delete(memory_id):
    """메모리 삭제"""
    connection = current_user.get_couple_connection()
    memory = Memory.query.filter_by(id=memory_id, couple_id=connection.id).first_or_404()
    
    # 작성자만 삭제 가능
    if memory.created_by != current_user.id:
        flash('자신이 작성한 추억만 삭제할 수 있습니다.', 'error')
        return redirect(url_for('memories.detail', memory_id=memory_id))
    
    try:
        # 이미지 파일 삭제
        memory.delete_image()
        
        # 데이터베이스에서 삭제
        db.session.delete(memory)
        db.session.commit()
        
        flash('추억이 성공적으로 삭제되었습니다.', 'success')
        return redirect(url_for('memories.index'))
    except Exception as e:
        db.session.rollback()
        flash('추억 삭제 중 오류가 발생했습니다.', 'error')
        current_app.logger.error(f"Memory deletion error: {e}")
        return redirect(url_for('memories.detail', memory_id=memory_id))

@memories_bp.route('/search')
@login_required
@couple_relationship_required
def search():
    """메모리 검색"""
    # 검색어 입력 정제 및 검증
    query = sanitize_input(request.args.get('q', '').strip(), max_length=100)
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    # 페이지 번호 검증
    if page < 1:
        page = 1
    
    connection = current_user.get_couple_connection()
    
    if query and len(query) >= 2:  # 최소 2글자 이상 검색
        # 제목과 내용에서 검색
        memories = Memory.query.filter_by(couple_id=connection.id)\
                              .filter(db.or_(
                                  Memory.title.contains(query),
                                  Memory.content.contains(query)
                              ))\
                              .order_by(Memory.memory_date.desc(), Memory.created_at.desc())\
                              .paginate(page=page, per_page=per_page, error_out=False)
    else:
        memories = Memory.query.filter_by(couple_id=connection.id)\
                              .order_by(Memory.memory_date.desc(), Memory.created_at.desc())\
                              .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('memories/search.html', memories=memories, query=query)

@memories_bp.route('/api/stats')
@login_required
@couple_relationship_required
def api_stats():
    """메모리 통계 API"""
    connection = current_user.get_couple_connection()
    
    # 총 메모리 수
    total_memories = Memory.query.filter_by(couple_id=connection.id).count()
    
    # 이번 달 메모리 수
    today = date.today()
    this_month_start = date(today.year, today.month, 1)
    this_month_memories = Memory.query.filter_by(couple_id=connection.id)\
                                     .filter(Memory.memory_date >= this_month_start)\
                                     .count()
    
    # 이미지가 있는 메모리 수
    memories_with_images = Memory.query.filter_by(couple_id=connection.id)\
                                      .filter(Memory.image_path.isnot(None))\
                                      .filter(Memory.image_path != '')\
                                      .count()
    
    return jsonify({
        'total_memories': total_memories,
        'this_month_memories': this_month_memories,
        'memories_with_images': memories_with_images
    })