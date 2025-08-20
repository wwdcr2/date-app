"""테스트 설정 및 픽스처"""

import pytest
import tempfile
import os
from datetime import datetime, date
from app.create_app import create_app
from app.extensions import db
from app.models.user import User
from app.models.couple import CoupleConnection
from app.models.dday import DDay
from app.models.event import Event
from app.models.question import Question, DailyQuestion, Answer
from app.models.memory import Memory
from app.models.mood import MoodEntry
from app.models.notification import Notification

@pytest.fixture
def app():
    """테스트용 Flask 애플리케이션 생성"""
    # 임시 데이터베이스 파일 생성
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key',
        'UPLOAD_FOLDER': tempfile.gettempdir(),
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB
        'ALLOWED_EXTENSIONS': {'png', 'jpg', 'jpeg', 'gif'}
    })
    
    with app.app_context():
        db.create_all()
        yield app
        
    # 정리
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """테스트 클라이언트"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """CLI 러너"""
    return app.test_cli_runner()

@pytest.fixture
def test_user():
    """테스트용 사용자 ID 반환"""
    return 1

@pytest.fixture
def test_partner():
    """테스트용 파트너 ID 반환"""
    return 2

@pytest.fixture
def test_couple():
    """테스트용 커플 연결 ID 반환"""
    return 1

@pytest.fixture
def test_dday(app, test_couple, test_user):
    """테스트용 D-Day 생성"""
    with app.app_context():
        dday = DDay(
            couple_id=test_couple.id,
            title='테스트 기념일',
            target_date=date(2024, 12, 25),
            description='테스트용 D-Day',
            created_by=test_user.id
        )
        db.session.add(dday)
        db.session.commit()
        return dday

@pytest.fixture
def test_event(app, test_couple, test_user):
    """테스트용 이벤트 생성"""
    with app.app_context():
        event = Event(
            couple_id=test_couple.id,
            title='테스트 일정',
            description='테스트용 일정',
            start_datetime=datetime(2024, 1, 1, 10, 0),
            end_datetime=datetime(2024, 1, 1, 12, 0),
            participant_type='both',
            created_by=test_user.id
        )
        db.session.add(event)
        db.session.commit()
        return event

@pytest.fixture
def test_question(app):
    """테스트용 질문 생성"""
    with app.app_context():
        question = Question(
            text='당신의 취미는 무엇인가요?',
            category='일상',
            difficulty='easy'
        )
        db.session.add(question)
        db.session.commit()
        return question

@pytest.fixture
def authenticated_client(client, test_user):
    """인증된 클라이언트"""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_user.id)
        sess['_fresh'] = True
    return client