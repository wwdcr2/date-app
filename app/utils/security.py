"""보안 관련 유틸리티 및 미들웨어"""

import os
import re
from functools import wraps
from flask import request, jsonify, current_app, abort, flash, redirect, url_for
from flask_login import current_user
from werkzeug.utils import secure_filename
from PIL import Image

# python-magic을 선택적으로 import (시스템에 libmagic이 없을 수 있음)
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False


class SecurityMiddleware:
    """보안 관련 미들웨어 클래스"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Flask 애플리케이션에 보안 미들웨어 초기화"""
        app.before_request(self.validate_request)
        app.after_request(self.add_security_headers)
    
    def validate_request(self):
        """요청 검증"""
        # 파일 업로드 크기 제한 검사
        if request.content_length and request.content_length > current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024):
            abort(413)  # Request Entity Too Large
        
        # 악성 요청 패턴 검사
        if self._is_malicious_request():
            abort(400)  # Bad Request
    
    def add_security_headers(self, response):
        """보안 헤더 추가"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # HTTPS 환경에서만 HSTS 헤더 추가
        if request.is_secure:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response
    
    def _is_malicious_request(self):
        """악성 요청 패턴 검사"""
        # SQL 인젝션 패턴 검사
        sql_patterns = [
            r'(\bunion\b.*\bselect\b)',
            r'(\bselect\b.*\bfrom\b)',
            r'(\binsert\b.*\binto\b)',
            r'(\bdelete\b.*\bfrom\b)',
            r'(\bdrop\b.*\btable\b)',
            r'(\bupdate\b.*\bset\b)'
        ]
        
        # XSS 패턴 검사
        xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>.*?</iframe>'
        ]
        
        # 요청 데이터 검사
        request_data = ''
        if request.args:
            request_data += str(request.args)
        if request.form:
            request_data += str(request.form)
        if request.json:
            request_data += str(request.json)
        
        request_data = request_data.lower()
        
        # 패턴 매칭
        all_patterns = sql_patterns + xss_patterns
        for pattern in all_patterns:
            if re.search(pattern, request_data, re.IGNORECASE):
                current_app.logger.warning(f"Malicious request detected: {pattern}")
                return True
        
        return False


def couple_relationship_required(f):
    """커플 관계 검증이 필요한 엔드포인트에 사용하는 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.is_json:
                return jsonify({'error': '로그인이 필요합니다.'}), 401
            flash('로그인이 필요합니다.', 'error')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_connected_to_partner():
            if request.is_json:
                return jsonify({'error': '파트너와 연결된 후 이용할 수 있습니다.'}), 403
            flash('파트너와 연결된 후 이용할 수 있습니다.', 'error')
            return redirect(url_for('couple.connect'))
        
        return f(*args, **kwargs)
    return decorated_function


def validate_couple_access(resource_couple_id):
    """커플 리소스 접근 권한 검증"""
    if not current_user.is_authenticated:
        return False
    
    user_couple = current_user.get_couple_connection()
    if not user_couple:
        return False
    
    return user_couple.id == resource_couple_id


def sanitize_input(text, max_length=None):
    """입력 데이터 정제"""
    if not text:
        return text
    
    # 문자열로 변환
    text = str(text)
    
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    
    # 특수 문자 이스케이프 (순서 중요)
    text = text.replace('&', '&amp;')  # & 먼저 처리
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    text = text.replace('"', '&quot;').replace("'", '&#x27;')
    
    # 앞뒤 공백 제거
    text = text.strip()
    
    # 길이 제한
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text


class FileUploadValidator:
    """파일 업로드 보안 검증 클래스"""
    
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    MAX_IMAGE_DIMENSION = 2048  # 최대 이미지 크기 (픽셀)
    
    @classmethod
    def validate_file(cls, file):
        """파일 검증"""
        errors = []
        
        if not file or not file.filename:
            errors.append('파일이 선택되지 않았습니다.')
            return errors
        
        # 파일명 검증
        if not cls._is_allowed_filename(file.filename):
            errors.append('허용되지 않는 파일 형식입니다.')
        
        # 파일 크기 검증
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > cls.MAX_FILE_SIZE:
            errors.append(f'파일 크기가 너무 큽니다. (최대 {cls.MAX_FILE_SIZE // (1024*1024)}MB)')
        
        # MIME 타입 검증
        if not cls._is_allowed_mime_type(file):
            errors.append('허용되지 않는 파일 타입입니다.')
        
        # 이미지 파일인 경우 추가 검증
        if cls._is_image_file(file.filename):
            image_errors = cls._validate_image(file)
            errors.extend(image_errors)
        
        return errors
    
    @classmethod
    def _is_allowed_filename(cls, filename):
        """파일명 확장자 검증"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in cls.ALLOWED_EXTENSIONS
    
    @classmethod
    def _is_allowed_mime_type(cls, file):
        """MIME 타입 검증"""
        if not HAS_MAGIC:
            # python-magic이 없는 경우 기본 검증만 수행
            return True
        
        try:
            # python-magic을 사용하여 실제 파일 타입 검증
            file_content = file.read(1024)  # 첫 1KB만 읽어서 검증
            file.seek(0)  # 파일 포인터 리셋
            
            mime_type = magic.from_buffer(file_content, mime=True)
            allowed_mime_types = {
                'image/png', 'image/jpeg', 'image/gif', 'image/webp'
            }
            
            return mime_type in allowed_mime_types
        except Exception:
            # 오류 발생 시 기본 검증만 수행
            return True
    
    @classmethod
    def _is_image_file(cls, filename):
        """이미지 파일 여부 확인"""
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        return ext in {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    @classmethod
    def _validate_image(cls, file):
        """이미지 파일 추가 검증"""
        errors = []
        
        try:
            # PIL을 사용하여 이미지 검증
            image = Image.open(file)
            
            # 이미지 크기 검증
            width, height = image.size
            if width > cls.MAX_IMAGE_DIMENSION or height > cls.MAX_IMAGE_DIMENSION:
                errors.append(f'이미지 크기가 너무 큽니다. (최대 {cls.MAX_IMAGE_DIMENSION}x{cls.MAX_IMAGE_DIMENSION})')
            
            # 이미지 형식 검증
            if image.format.lower() not in ['png', 'jpeg', 'gif', 'webp']:
                errors.append('지원되지 않는 이미지 형식입니다.')
            
            # 파일 포인터 리셋
            file.seek(0)
            
        except Exception as e:
            errors.append('유효하지 않은 이미지 파일입니다.')
            file.seek(0)
        
        return errors
    
    @classmethod
    def secure_save_file(cls, file, upload_folder):
        """안전한 파일 저장"""
        if not file or not file.filename:
            return None, ['파일이 없습니다.']
        
        # 파일 검증
        errors = cls.validate_file(file)
        if errors:
            return None, errors
        
        # 안전한 파일명 생성
        filename = secure_filename(file.filename)
        
        # 파일명 중복 방지
        base_name, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(os.path.join(upload_folder, filename)):
            filename = f"{base_name}_{counter}{ext}"
            counter += 1
        
        # 파일 저장
        try:
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            # 이미지 파일인 경우 최적화
            if cls._is_image_file(filename):
                cls._optimize_image(file_path)
            
            return filename, []
        
        except Exception as e:
            current_app.logger.error(f"File save error: {e}")
            return None, ['파일 저장 중 오류가 발생했습니다.']
    
    @classmethod
    def _optimize_image(cls, file_path):
        """이미지 최적화"""
        try:
            with Image.open(file_path) as image:
                # EXIF 데이터 제거 (보안상 이유)
                if hasattr(image, '_getexif'):
                    image = image.copy()
                
                # 이미지 크기 조정 (필요한 경우)
                if image.size[0] > cls.MAX_IMAGE_DIMENSION or image.size[1] > cls.MAX_IMAGE_DIMENSION:
                    image.thumbnail((cls.MAX_IMAGE_DIMENSION, cls.MAX_IMAGE_DIMENSION), Image.Resampling.LANCZOS)
                
                # 최적화된 이미지 저장
                image.save(file_path, optimize=True, quality=85)
        
        except Exception as e:
            current_app.logger.warning(f"Image optimization failed: {e}")


def validate_form_data(data, rules):
    """폼 데이터 검증"""
    errors = {}
    
    for field, field_rules in rules.items():
        value = data.get(field, '')
        field_errors = []
        
        # 필수 필드 검증
        if field_rules.get('required', False) and not value:
            field_errors.append(f'{field}는 필수 입력 항목입니다.')
        
        if value:  # 값이 있는 경우에만 추가 검증
            # 길이 검증
            if 'min_length' in field_rules and len(value) < field_rules['min_length']:
                field_errors.append(f'{field}는 최소 {field_rules["min_length"]}자 이상이어야 합니다.')
            
            if 'max_length' in field_rules and len(value) > field_rules['max_length']:
                field_errors.append(f'{field}는 최대 {field_rules["max_length"]}자까지 입력 가능합니다.')
            
            # 패턴 검증
            if 'pattern' in field_rules:
                if not re.match(field_rules['pattern'], value):
                    field_errors.append(field_rules.get('pattern_message', f'{field} 형식이 올바르지 않습니다.'))
            
            # 커스텀 검증 함수
            if 'validator' in field_rules:
                custom_error = field_rules['validator'](value)
                if custom_error:
                    field_errors.append(custom_error)
        
        if field_errors:
            errors[field] = field_errors
    
    return errors