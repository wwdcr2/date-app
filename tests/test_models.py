"""모델 단위 테스트"""

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

class TestUserModel:
    """사용자 모델 테스트"""
    
    def test_user_creation(self, app):
        """사용자 생성 테스트"""
        with app.app_context():
            user = User(
                email='test@example.com',
                name='테스트 사용자'
            )
            user.set_password('testpassword')
            
            assert user.email == 'test@example.com'
            assert user.name == '테스트 사용자'
            assert user.password_hash is not None
            assert user.password_hash != 'testpassword'
    
    def test_password_hashing(self, app):
        """비밀번호 해싱 테스트"""
        with app.app_context():
            user = User(email='test@example.com', name='테스트')
            user.set_password('testpassword')
            
            assert user.check_password('testpassword') is True
            assert user.check_password('wrongpassword') is False
    
    def test_user_repr(self, app):
        """사용자 문자열 표현 테스트"""
        with app.app_context():
            user = User(email='test@example.com', name='테스트')
            assert repr(user) == '<User test@example.com>'
    
    def test_get_couple_connection(self, app):
        """커플 연결 조회 테스트"""
        with app.app_context():
            # 테스트 데이터 생성
            user = User(email='test@example.com', name='테스트 사용자')
            user.set_password('testpassword')
            partner = User(email='partner@example.com', name='파트너 사용자')
            partner.set_password('partnerpassword')
            
            db.session.add(user)
            db.session.add(partner)
            db.session.commit()
            
            connection = CoupleConnection(
                user1_id=user.id,
                user2_id=partner.id,
                invite_code='TEST01'
            )
            db.session.add(connection)
            db.session.commit()
            
            # 테스트 실행
            user_connection = user.get_couple_connection()
            assert user_connection is not None
            assert user_connection.id == connection.id
    
    def test_get_partner(self, app, test_user, test_partner, test_couple):
        """파트너 조회 테스트"""
        with app.app_context():
            partner = test_user.get_partner()
            assert partner is not None
            assert partner.id == test_partner.id
            assert partner.email == test_partner.email
    
    def test_is_connected_to_partner(self, app, test_user, test_couple):
        """파트너 연결 상태 확인 테스트"""
        with app.app_context():
            assert test_user.is_connected_to_partner() is True
            
            # 연결되지 않은 사용자
            single_user = User(email='single@example.com', name='싱글')
            db.session.add(single_user)
            db.session.commit()
            
            assert single_user.is_connected_to_partner() is False

class TestCoupleConnectionModel:
    """커플 연결 모델 테스트"""
    
    def test_couple_connection_creation(self, app):
        """커플 연결 생성 테스트"""
        with app.app_context():
            connection = CoupleConnection(
                user1_id=1,
                user2_id=2,
                invite_code='TEST01'
            )
            
            assert connection.user1_id == 1
            assert connection.user2_id == 2
            assert connection.invite_code == 'TEST01'
    
    def test_generate_invite_code(self, app):
        """초대 코드 생성 테스트"""
        with app.app_context():
            code = CoupleConnection.generate_invite_code()
            
            assert len(code) == 6
            assert code.isupper()
            assert code.isalnum()
    
    def test_get_users(self, app, test_user, test_partner, test_couple):
        """커플 사용자 조회 테스트"""
        with app.app_context():
            user1, user2 = test_couple.get_users()
            
            assert user1.id == test_user.id
            assert user2.id == test_partner.id
    
    def test_get_partner_of(self, app, test_user, test_partner, test_couple):
        """특정 사용자의 파트너 조회 테스트"""
        with app.app_context():
            partner = test_couple.get_partner_of(test_user.id)
            assert partner.id == test_partner.id
            
            partner = test_couple.get_partner_of(test_partner.id)
            assert partner.id == test_user.id
            
            # 존재하지 않는 사용자
            partner = test_couple.get_partner_of(999)
            assert partner is None

class TestDDayModel:
    """D-Day 모델 테스트"""
    
    def test_dday_creation(self, app, test_couple, test_user):
        """D-Day 생성 테스트"""
        with app.app_context():
            dday = DDay(
                couple_id=test_couple.id,
                title='테스트 기념일',
                target_date=date(2024, 12, 25),
                description='테스트용 D-Day',
                created_by=test_user.id
            )
            
            assert dday.title == '테스트 기념일'
            assert dday.target_date == date(2024, 12, 25)
            assert dday.description == '테스트용 D-Day'
    
    def test_days_remaining_future(self, app, test_couple, test_user):
        """미래 날짜 D-Day 계산 테스트"""
        with app.app_context():
            future_date = date.today() + timedelta(days=10)
            dday = DDay(
                couple_id=test_couple.id,
                title='미래 기념일',
                target_date=future_date,
                created_by=test_user.id
            )
            
            assert dday.days_remaining() == 10
            assert dday.is_past() is False
            assert dday.is_today() is False
            assert dday.get_status_text() == 'D-10'
    
    def test_days_remaining_past(self, app, test_couple, test_user):
        """과거 날짜 D-Day 계산 테스트"""
        with app.app_context():
            past_date = date.today() - timedelta(days=5)
            dday = DDay(
                couple_id=test_couple.id,
                title='과거 기념일',
                target_date=past_date,
                created_by=test_user.id
            )
            
            assert dday.days_remaining() == -5
            assert dday.is_past() is True
            assert dday.is_today() is False
            assert dday.get_status_text() == 'D+5'
    
    def test_days_remaining_today(self, app, test_couple, test_user):
        """오늘 날짜 D-Day 계산 테스트"""
        with app.app_context():
            today = date.today()
            dday = DDay(
                couple_id=test_couple.id,
                title='오늘 기념일',
                target_date=today,
                created_by=test_user.id
            )
            
            assert dday.days_remaining() == 0
            assert dday.is_past() is False
            assert dday.is_today() is True
            assert dday.get_status_text() == 'D-Day'

class TestEventModel:
    """이벤트 모델 테스트"""
    
    def test_event_creation(self, app, test_couple, test_user):
        """이벤트 생성 테스트"""
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
            
            assert event.title == '테스트 일정'
            assert event.participant_type == 'both'
    
    def test_participant_color(self, app, test_couple, test_user):
        """참여자 색상 테스트"""
        with app.app_context():
            event_male = Event(
                couple_id=test_couple.id,
                title='남성 일정',
                start_datetime=datetime(2024, 1, 1, 10, 0),
                end_datetime=datetime(2024, 1, 1, 12, 0),
                participant_type='male',
                created_by=test_user.id
            )
            
            event_female = Event(
                couple_id=test_couple.id,
                title='여성 일정',
                start_datetime=datetime(2024, 1, 1, 10, 0),
                end_datetime=datetime(2024, 1, 1, 12, 0),
                participant_type='female',
                created_by=test_user.id
            )
            
            event_both = Event(
                couple_id=test_couple.id,
                title='함께 일정',
                start_datetime=datetime(2024, 1, 1, 10, 0),
                end_datetime=datetime(2024, 1, 1, 12, 0),
                participant_type='both',
                created_by=test_user.id
            )
            
            assert event_male.get_participant_color() == '#B8E6E1'
            assert event_female.get_participant_color() == '#F8BBD9'
            assert event_both.get_participant_color() == '#FFB5A7'
    
    def test_participant_text(self, app, test_couple, test_user):
        """참여자 텍스트 테스트"""
        with app.app_context():
            event = Event(
                couple_id=test_couple.id,
                title='테스트 일정',
                start_datetime=datetime(2024, 1, 1, 10, 0),
                end_datetime=datetime(2024, 1, 1, 12, 0),
                participant_type='both',
                created_by=test_user.id
            )
            
            assert event.get_participant_text() == '함께'
    
    def test_duration_calculation(self, app, test_couple, test_user):
        """이벤트 기간 계산 테스트"""
        with app.app_context():
            # 2시간 이벤트
            event_2h = Event(
                couple_id=test_couple.id,
                title='2시간 일정',
                start_datetime=datetime(2024, 1, 1, 10, 0),
                end_datetime=datetime(2024, 1, 1, 12, 0),
                participant_type='both',
                created_by=test_user.id
            )
            
            # 30분 이벤트
            event_30m = Event(
                couple_id=test_couple.id,
                title='30분 일정',
                start_datetime=datetime(2024, 1, 1, 10, 0),
                end_datetime=datetime(2024, 1, 1, 10, 30),
                participant_type='both',
                created_by=test_user.id
            )
            
            assert event_2h.get_duration_text() == '2시간'
            assert event_30m.get_duration_text() == '30분'

class TestQuestionModel:
    """질문 모델 테스트"""
    
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
    
    def test_daily_question_creation(self, app, test_couple, test_question):
        """일일 질문 생성 테스트"""
        with app.app_context():
            daily_question = DailyQuestion(
                couple_id=test_couple.id,
                question_id=test_question.id,
                date=date.today()
            )
            
            assert daily_question.couple_id == test_couple.id
            assert daily_question.question_id == test_question.id
            assert daily_question.user1_answered is False
            assert daily_question.user2_answered is False
    
    def test_answer_creation(self, app, test_user):
        """답변 생성 테스트"""
        with app.app_context():
            answer = Answer(
                question_id=1,
                user_id=test_user.id,
                answer_text='저는 독서를 좋아합니다.'
            )
            
            assert answer.user_id == test_user.id
            assert answer.answer_text == '저는 독서를 좋아합니다.'

class TestMoodEntryModel:
    """무드 엔트리 모델 테스트"""
    
    def test_mood_entry_creation(self, app, test_user):
        """무드 엔트리 생성 테스트"""
        with app.app_context():
            mood = MoodEntry(
                user_id=test_user.id,
                mood_level=4,
                note='오늘은 기분이 좋아요!',
                date=date.today()
            )
            
            assert mood.user_id == test_user.id
            assert mood.mood_level == 4
            assert mood.note == '오늘은 기분이 좋아요!'
    
    def test_mood_level_validation(self, app, test_user):
        """무드 레벨 유효성 검사 테스트"""
        with app.app_context():
            # 유효한 범위 (1-5)
            for level in range(1, 6):
                mood = MoodEntry(
                    user_id=test_user.id,
                    mood_level=level,
                    date=date.today()
                )
                assert mood.mood_level == level

class TestMemoryModel:
    """메모리 모델 테스트"""
    
    def test_memory_creation(self, app, test_couple, test_user):
        """메모리 생성 테스트"""
        with app.app_context():
            memory = Memory(
                couple_id=test_couple.id,
                title='첫 데이트',
                content='처음 만난 날의 추억',
                memory_date=date(2023, 1, 1),
                created_by=test_user.id
            )
            
            assert memory.title == '첫 데이트'
            assert memory.content == '처음 만난 날의 추억'
            assert memory.memory_date == date(2023, 1, 1)

class TestNotificationModel:
    """알림 모델 테스트"""
    
    def test_notification_creation(self, app, test_user):
        """알림 생성 테스트"""
        with app.app_context():
            notification = Notification(
                user_id=test_user.id,
                type='mood_update',
                title='기분 공유',
                content='파트너가 기분을 공유했습니다.'
            )
            
            assert notification.user_id == test_user.id
            assert notification.type == 'mood_update'
            assert notification.title == '기분 공유'
            assert notification.is_read is False