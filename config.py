import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    """기본 설정 클래스"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-this'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///couple_app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 파일 업로드 설정
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB 최대 파일 크기 (보안 강화)
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # SocketIO 설정
    SOCKETIO_ASYNC_MODE = 'threading'
    
    # 보안 설정 (일시적으로 비활성화)
    WTF_CSRF_ENABLED = False
    WTF_CSRF_TIME_LIMIT = 3600  # CSRF 토큰 유효시간 (1시간)
    SESSION_COOKIE_SECURE = False  # 개발환경에서는 False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 세션 유효시간 (24시간)

class DevelopmentConfig(Config):
    """개발 환경 설정"""
    DEBUG = True
    SQLALCHEMY_ECHO = True  # SQL 쿼리 로깅

class ProductionConfig(Config):
    """프로덕션 환경 설정"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    SESSION_COOKIE_SECURE = True  # HTTPS 환경에서만 쿠키 전송
    
    # 성능 최적화 설정
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 0
    }
    
    # 정적 파일 캐싱 설정
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1년 (정적 파일)
    
    # 압축 설정
    COMPRESS_MIMETYPES = [
        'text/html',
        'text/css',
        'text/xml',
        'application/json',
        'application/javascript',
        'application/xml+rss',
        'application/atom+xml',
        'image/svg+xml'
    ]
    
    # 보안 강화
    PREFERRED_URL_SCHEME = 'https'
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # 로깅 설정
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/couple_app.log'

class TestingConfig(Config):
    """테스트 환경 설정"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# 환경별 설정 매핑
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}