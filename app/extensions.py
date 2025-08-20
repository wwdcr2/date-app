"""Flask 확장 모듈들을 초기화하는 파일"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_wtf.csrf import CSRFProtect

# 확장 모듈 인스턴스 생성
db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO()
csrf = CSRFProtect()

def init_extensions(app):
    """Flask 애플리케이션에 확장 모듈들을 초기화"""
    
    # SQLAlchemy 초기화
    db.init_app(app)
    
    # Flask-Login 초기화
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '로그인이 필요합니다.'
    login_manager.login_message_category = 'info'
    
    # User loader 함수 등록
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
    
    # CSRF 보호 초기화 (일시적으로 비활성화)
    # csrf.init_app(app)
    
    # 보안 미들웨어 초기화 (일시적으로 비활성화)
    # from app.utils.security import SecurityMiddleware
    # SecurityMiddleware(app)
    
    # SocketIO 초기화
    socketio.init_app(app, 
                     async_mode=app.config.get('SOCKETIO_ASYNC_MODE', 'threading'),
                     cors_allowed_origins="*")
    
    return app