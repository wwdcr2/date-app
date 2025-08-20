"""기본 테스트 코드"""

import pytest
from datetime import datetime, date, timedelta
from app.models.user import User
from app.models.couple import CoupleConnection
from app.models.dday import DDay
from app.models.event import Event
from app.models.question import Question, DailyQuestion, Answer
from app.models.memory import Memory
from app.models.mood import MoodEntry
from app.models.notification import Notification
from app.extensions import db

class TestBasicModels:
    """기본 모델 테스트"""
    
    def test_user_creation_and_password(self, app):
        """사용자 생성 및 비밀번호 테스트"""
        with app.app_context():
            user = User(
                email='test@example.com',
                name='테스트 사용자'
            )
            user.set_password('testpassword')
            
            assert user.email == 'test@example.com'
            assert user.name == '테스트 사용자'
            assert user.check_password('testpassword') is True
            assert user.check_password('wrongpassword') is False
    
    def test_dday_calculation(self, app):
        """D-Day 계산 테스트"""
        with app.app_context():
            # 미래 날짜
            future_date = date.today() + timedelta(days=10)
            dday = DDay(
                couple_id=1,
                title='미래 기념일',
                target_date=future_date,
                created_by=1
            )
            
            assert dday.days_remaining() == 10
            assert dday.is_past() is False
            assert dday.get_status_text() == 'D-10'
            
            # 과거 날짜
            past_date = date.today() - timedelta(days=5)
            dday_past = DDay(
                couple_id=1,
                title='과거 기념일',
                target_date=past_date,
                created_by=1
            )
            
            assert dday_past.days_remaining() == -5
            assert dday_past.is_past() is True
            assert dday_past.get_status_text() == 'D+5'
    
    def test_event_participant_colors(self, app):
        """이벤트 참여자 색상 테스트"""
        with app.app_context():
            event_male = Event(
                couple_id=1,
                title='남성 일정',
                start_datetime=datetime(2024, 1, 1, 10, 0),
                end_datetime=datetime(2024, 1, 1, 12, 0),
                participant_type='male',
                created_by=1
            )
            
            event_female = Event(
                couple_id=1,
                title='여성 일정',
                start_datetime=datetime(2024, 1, 1, 10, 0),
                end_datetime=datetime(2024, 1, 1, 12, 0),
                participant_type='female',
                created_by=1
            )
            
            event_both = Event(
                couple_id=1,
                title='함께 일정',
                start_datetime=datetime(2024, 1, 1, 10, 0),
                end_datetime=datetime(2024, 1, 1, 12, 0),
                participant_type='both',
                created_by=1
            )
            
            assert event_male.get_participant_color() == '#B8E6E1'
            assert event_female.get_participant_color() == '#F8BBD9'
            assert event_both.get_participant_color() == '#FFB5A7'
    
    def test_mood_entry_emoji(self, app):
        """무드 엔트리 이모지 테스트"""
        with app.app_context():
            mood_levels = [1, 2, 3, 4, 5]
            expected_emojis = ['😢', '😞', '😐', '😊', '😍']
            
            for level, expected_emoji in zip(mood_levels, expected_emojis):
                mood = MoodEntry(
                    user_id=1,
                    mood_level=level,
                    date=date.today()
                )
                assert mood.get_mood_emoji() == expected_emoji
    
    def test_question_creation(self, app):
        """질문 생성 테스트"""
        with app.app_context():
            question = Question(
                text='당신의 취미는 무엇인가요?',
                category='일상',
                difficulty='easy'
            )
            
            assert question.text == '당신의 취미는 무엇인가요?'
            assert question.category == '일상'
            assert question.difficulty == 'easy'
    
    def test_memory_creation(self, app):
        """메모리 생성 테스트"""
        with app.app_context():
            memory = Memory(
                couple_id=1,
                title='첫 데이트',
                content='처음 만난 날의 추억',
                memory_date=date(2023, 1, 1),
                created_by=1
            )
            
            assert memory.title == '첫 데이트'
            assert memory.content == '처음 만난 날의 추억'
            assert memory.memory_date == date(2023, 1, 1)
    
    def test_notification_creation(self, app):
        """알림 생성 테스트"""
        with app.app_context():
            notification = Notification(
                user_id=1,
                type='mood_update',
                title='기분 공유',
                content='파트너가 기분을 공유했습니다.'
            )
            
            assert notification.user_id == 1
            assert notification.type == 'mood_update'
            assert notification.title == '기분 공유'
            # 데이터베이스에 저장하지 않은 상태에서는 기본값이 None일 수 있음
            assert notification.is_read is False or notification.is_read is None
    
    def test_couple_connection_invite_code(self, app):
        """커플 연결 초대 코드 테스트"""
        with app.app_context():
            code = CoupleConnection.generate_invite_code()
            
            assert len(code) == 6
            assert code.isupper()
            assert code.isalnum()

class TestDatabaseOperations:
    """데이터베이스 작업 테스트"""
    
    def test_user_crud_operations(self, app):
        """사용자 CRUD 작업 테스트"""
        with app.app_context():
            # Create
            user = User(
                email='crud@example.com',
                name='CRUD 테스트'
            )
            user.set_password('testpassword')
            db.session.add(user)
            db.session.commit()
            
            # Read
            saved_user = User.query.filter_by(email='crud@example.com').first()
            assert saved_user is not None
            assert saved_user.name == 'CRUD 테스트'
            
            # Update
            saved_user.name = '수정된 이름'
            db.session.commit()
            
            updated_user = User.query.get(saved_user.id)
            assert updated_user.name == '수정된 이름'
            
            # Delete
            user_id = saved_user.id
            db.session.delete(saved_user)
            db.session.commit()
            
            deleted_user = User.query.get(user_id)
            assert deleted_user is None
    
    def test_dday_crud_operations(self, app):
        """D-Day CRUD 작업 테스트"""
        with app.app_context():
            # 사용자 생성
            user = User(email='dday@example.com', name='D-Day 테스트')
            user.set_password('testpassword')
            db.session.add(user)
            db.session.commit()
            
            # 커플 연결 생성
            connection = CoupleConnection(
                user1_id=user.id,
                user2_id=user.id,  # 테스트용으로 같은 사용자
                invite_code='DDAY01'
            )
            db.session.add(connection)
            db.session.commit()
            
            # D-Day 생성
            dday = DDay(
                couple_id=connection.id,
                title='테스트 기념일',
                target_date=date(2024, 12, 25),
                description='테스트용 D-Day',
                created_by=user.id
            )
            db.session.add(dday)
            db.session.commit()
            
            # 조회
            saved_dday = DDay.query.filter_by(title='테스트 기념일').first()
            assert saved_dday is not None
            assert saved_dday.target_date == date(2024, 12, 25)
            
            # 수정
            saved_dday.title = '수정된 기념일'
            db.session.commit()
            
            updated_dday = DDay.query.get(saved_dday.id)
            assert updated_dday.title == '수정된 기념일'
            
            # 삭제
            dday_id = saved_dday.id
            db.session.delete(saved_dday)
            db.session.commit()
            
            deleted_dday = DDay.query.get(dday_id)
            assert deleted_dday is None