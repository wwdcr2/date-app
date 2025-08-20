"""Flask 애플리케이션 팩토리"""

import os
from flask import Flask
from config import config
from app.extensions import init_extensions

def create_app(config_name=None):
    """Flask 애플리케이션을 생성하고 설정하는 팩토리 함수"""
    
    # Flask 애플리케이션 인스턴스 생성
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # 설정 로드
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    # 테스트에서 딕셔너리를 직접 전달하는 경우 처리
    if isinstance(config_name, dict):
        app.config.update(config_name)
    else:
        from config import config
        app.config.from_object(config[config_name])
    
    # 확장 모듈 초기화
    init_extensions(app)
    
    # 업로드 폴더 생성
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    # 커스텀 필터 등록
    from app.utils.filters import register_filters
    register_filters(app)
    
    # 블루프린트 등록
    register_blueprints(app)
    
    # SocketIO 이벤트 등록
    register_socketio_events(app)
    
    # 성능 최적화 기능 초기화 (프로덕션 환경에서만)
    if config_name == 'production' or (isinstance(config_name, dict) and not config_name.get('DEBUG', True)):
        init_production_optimizations(app)
    
    return app

def register_blueprints(app):
    """블루프린트들을 등록하는 함수"""
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.couple import couple_bp
    from app.routes.dday import dday_bp
    from app.routes.calendar import calendar_bp
    from app.routes.questions import questions_bp
    from app.routes.memories import memories_bp
    from app.routes.mood import mood_bp
    from app.routes.notifications import notifications_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(couple_bp, url_prefix='/couple')
    app.register_blueprint(dday_bp, url_prefix='/dday')
    app.register_blueprint(calendar_bp, url_prefix='/calendar')
    app.register_blueprint(questions_bp, url_prefix='/questions')
    app.register_blueprint(memories_bp, url_prefix='/memories')
    app.register_blueprint(mood_bp, url_prefix='/mood')
    app.register_blueprint(notifications_bp, url_prefix='/notifications')

def register_socketio_events(app):
    """SocketIO 이벤트 핸들러 등록"""
    with app.app_context():
        import app.socketio_events

def init_production_optimizations(app):
    """프로덕션 환경 최적화 기능 초기화"""
    from app.utils.static_optimization import init_asset_versioning
    from app.utils.performance_monitoring import init_performance_monitoring
    from app.utils.db_optimization import optimize_database_settings
    
    # 자산 버전 관리 초기화
    init_asset_versioning(app)
    
    # 성능 모니터링 초기화
    init_performance_monitoring(app)
    
    # 데이터베이스 최적화 설정 적용
    with app.app_context():
        try:
            optimize_database_settings()
        except Exception as e:
            app.logger.warning(f"데이터베이스 최적화 설정 실패: {e}")