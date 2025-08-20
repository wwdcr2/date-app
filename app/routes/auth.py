"""인증 관련 라우트"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from app.models.user import User
from app.extensions import db
import re

# 블루프린트 생성
auth_bp = Blueprint('auth', __name__)

def is_valid_email(email):
    """이메일 형식 검증"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_password(password):
    """비밀번호 강도 검증 (최소 6자리)"""
    return len(password) >= 6

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """회원가입"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        print(f"Request content type: {request.content_type}")
        print(f"Request is_json: {request.is_json}")
        print(f"Request data: {request.data}")
        
        # JSON 요청 처리
        if request.is_json or request.content_type == 'application/json':
            try:
                data = request.get_json(force=True) or {}
                print(f"Parsed JSON data: {data}")
                email = data.get('email', '').strip().lower()
                password = data.get('password', '')
                name = data.get('name', '').strip()
            except Exception as e:
                print(f"JSON parsing error: {e}")
                # JSON 파싱 실패 시 폼 데이터로 처리
                email = request.form.get('email', '').strip().lower()
                password = request.form.get('password', '')
                name = request.form.get('name', '').strip()
        else:
            # 폼 요청 처리
            print(f"Form data: {dict(request.form)}")
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            name = request.form.get('name', '').strip()
        
        print(f"Extracted data - email: {email}, name: {name}, password: {'*' * len(password) if password else 'None'}")
        
        # 입력 검증
        errors = []
        
        if not email:
            errors.append('이메일을 입력해주세요.')
        elif not is_valid_email(email):
            errors.append('올바른 이메일 형식을 입력해주세요.')
        elif User.query.filter_by(email=email).first():
            errors.append('이미 사용 중인 이메일입니다.')
        
        if not password:
            errors.append('비밀번호를 입력해주세요.')
        elif not is_valid_password(password):
            errors.append('비밀번호는 최소 6자리 이상이어야 합니다.')
        
        if not name:
            errors.append('이름을 입력해주세요.')
        elif len(name) < 2:
            errors.append('이름은 최소 2자리 이상이어야 합니다.')
        
        if errors:
            if request.is_json:
                return jsonify({'success': False, 'errors': errors}), 400
            else:
                for error in errors:
                    flash(error, 'error')
                return render_template('auth/register.html')
        
        try:
            # 새 사용자 생성
            user = User(email=email, name=name)
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            # 자동 로그인
            login_user(user)
            
            if request.is_json:
                return jsonify({
                    'success': True, 
                    'message': '회원가입이 완료되었습니다.',
                    'redirect_url': url_for('main.index')
                })
            else:
                flash('회원가입이 완료되었습니다!', 'success')
                return redirect(url_for('main.index'))
                
        except Exception as e:
            db.session.rollback()
            error_msg = '회원가입 중 오류가 발생했습니다. 다시 시도해주세요.'
            
            if request.is_json:
                return jsonify({'success': False, 'errors': [error_msg]}), 500
            else:
                flash(error_msg, 'error')
                return render_template('auth/register.html')
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """로그인"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        # JSON 요청 처리
        if request.is_json or request.content_type == 'application/json':
            try:
                data = request.get_json(force=True) or {}
                email = data.get('email', '').strip().lower()
                password = data.get('password', '')
                remember_me = data.get('remember_me', False)
            except:
                # JSON 파싱 실패 시 폼 데이터로 처리
                email = request.form.get('email', '').strip().lower()
                password = request.form.get('password', '')
                remember_me = bool(request.form.get('remember_me'))
        else:
            # 폼 요청 처리
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            remember_me = bool(request.form.get('remember_me'))
        
        # 입력 검증
        errors = []
        
        if not email:
            errors.append('이메일을 입력해주세요.')
        if not password:
            errors.append('비밀번호를 입력해주세요.')
        
        if errors:
            if request.is_json:
                return jsonify({'success': False, 'errors': errors}), 400
            else:
                for error in errors:
                    flash(error, 'error')
                return render_template('auth/login.html')
        
        # 사용자 인증
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember_me)
            
            # 다음 페이지 처리
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('main.index')
            
            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': '로그인되었습니다.',
                    'redirect_url': next_page
                })
            else:
                flash('로그인되었습니다!', 'success')
                return redirect(next_page)
        else:
            error_msg = '이메일 또는 비밀번호가 올바르지 않습니다.'
            if request.is_json:
                return jsonify({'success': False, 'errors': [error_msg]}), 401
            else:
                flash(error_msg, 'error')
                return render_template('auth/login.html')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """로그아웃"""
    logout_user()
    flash('로그아웃되었습니다.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile')
@login_required
def profile():
    """프로필 페이지"""
    return render_template('auth/profile.html', user=current_user)

@auth_bp.route('/check-email')
def check_email():
    """이메일 중복 확인 (AJAX용)"""
    email = request.args.get('email', '').strip().lower()
    
    if not email:
        return jsonify({'available': False, 'message': '이메일을 입력해주세요.'})
    
    if not is_valid_email(email):
        return jsonify({'available': False, 'message': '올바른 이메일 형식을 입력해주세요.'})
    
    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({'available': False, 'message': '이미 사용 중인 이메일입니다.'})
    
    return jsonify({'available': True, 'message': '사용 가능한 이메일입니다.'})

@auth_bp.route('/api/user-info')
@login_required
def user_info():
    """현재 사용자 정보 반환 (API용)"""
    partner = current_user.get_partner()
    
    return jsonify({
        'id': current_user.id,
        'email': current_user.email,
        'name': current_user.name,
        'created_at': current_user.created_at.isoformat(),
        'is_connected': current_user.is_connected_to_partner(),
        'partner': {
            'id': partner.id,
            'name': partner.name,
            'email': partner.email
        } if partner else None
    })