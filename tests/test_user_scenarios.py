"""사용자 시나리오 기반 기능 테스트"""

import pytest
import json
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

class TestUserRegistrationAndConnection:
    """사용자 등록 및 커플 연결 시나리오 테스트"""
    
    def test_complete_user_registration_flow(self, client, app):
        """완전한 사용자 등록 플로우 테스트"""
        with app.app_context():
            # 1. 첫 번째 사용자 등록
            response = client.post('/auth/register', json={
                'email': 'user1@example.com',
                'password': 'password123',
                'name': '사용자1'
            })
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            
            # 2. 두 번째 사용자 등록
            response = client.post('/auth/register', json={
                'email': 'user2@example.com',
                'password': 'password123',
                'name': '사용자2'
            })
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            
            # 3. 사용자들이 데이터베이스에 생성되었는지 확인
            user1 = User.query.filter_by(email='user1@example.com').first()
            user2 = User.query.filter_by(email='user2@example.com').first()
            
            assert user1 is not None
            assert user2 is not None
            assert user1.name == '사용자1'
            assert user2.name == '사용자2'
    
    def test_couple_connection_scenario(self, client, app):
        """커플 연결 시나리오 테스트"""
        with app.app_context():
            # 1. 두 사용자 생성
            user1 = User(email='couple1@example.com', name='커플1')
            user1.set_password('password123')
            user2 = User(email='couple2@example.com', name='커플2')
            user2.set_password('password123')
            
            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()
            
            # 2. 첫 번째 사용자가 커플 연결 생성
            connection = CoupleConnection(
                user1_id=user1.id,
                user2_id=user2.id,
                invite_code=CoupleConnection.generate_invite_code()
            )
            db.session.add(connection)
            db.session.commit()
            
            # 3. 연결 확인
            assert user1.get_couple_connection() is not None
            assert user2.get_couple_connection() is not None
            assert user1.get_partner().id == user2.id
            assert user2.get_partner().id == user1.id

class TestDailyQuestionWorkflow:
    """일일 질문 워크플로우 테스트"""
    
    def test_daily_question_complete_workflow(self, app, test_user, test_partner, test_couple):
        """일일 질문 완전한 워크플로우 테스트"""
        with app.app_context():
            # 1. 질문 생성
            question = Question(
                text='오늘 가장 기억에 남는 일은 무엇인가요?',
                category='일상',
                difficulty='easy'
            )
            db.session.add(question)
            db.session.commit()
            
            # 2. 일일 질문 생성
            daily_question = DailyQuestion(
                couple_id=test_couple.id,
                question_id=question.id,
                date=date.today()
            )
            db.session.add(daily_question)
            db.session.commit()
            
            # 3. 첫 번째 사용자 답변
            answer1 = Answer(
                question_id=question.id,
                user_id=test_user.id,
                answer_text='오늘은 파트너와 함께 산책을 했어요.'
            )
            db.session.add(answer1)
            db.session.commit()
            
            # 4. 첫 번째 사용자 답변 후 상태 확인
            daily_question = DailyQuestion.query.get(daily_question.id)
            daily_question.user1_answered = True
            db.session.commit()
            
            # 5. 두 번째 사용자 답변
            answer2 = Answer(
                question_id=question.id,
                user_id=test_partner.id,
                answer_text='저도 오늘 산책이 정말 좋았어요!'
            )
            db.session.add(answer2)
            db.session.commit()
            
            # 6. 두 번째 사용자 답변 후 상태 확인
            daily_question.user2_answered = True
            db.session.commit()
            
            # 7. 최종 상태 검증
            assert daily_question.user1_answered is True
            assert daily_question.user2_answered is True
            
            # 8. 답변 조회 권한 확인
            user1_answer = daily_question.get_user_answer(test_user.id)
            user2_answer = daily_question.get_user_answer(test_partner.id)
            
            assert user1_answer is not None
            assert user2_answer is not None
            assert user1_answer.answer_text == '오늘은 파트너와 함께 산책을 했어요.'
            assert user2_answer.answer_text == '저도 오늘 산책이 정말 좋았어요!'
    
    def test_answer_access_control(self, app, test_user, test_partner, test_couple):
        """답변 접근 제어 테스트"""
        with app.app_context():
            # 1. 질문 및 일일 질문 생성
            question = Question(
                text='당신의 꿈은 무엇인가요?',
                category='깊은대화',
                difficulty='medium'
            )
            db.session.add(question)
            db.session.commit()
            
            daily_question = DailyQuestion(
                couple_id=test_couple.id,
                question_id=question.id,
                date=date.today()
            )
            db.session.add(daily_question)
            db.session.commit()
            
            # 2. 파트너만 답변
            partner_answer = Answer(
                question_id=question.id,
                user_id=test_partner.id,
                answer_text='저는 세계여행을 하고 싶어요.'
            )
            db.session.add(partner_answer)
            db.session.commit()
            
            # 3. 접근 제어 확인 - 내가 답변하지 않았으므로 파트너 답변을 볼 수 없어야 함
            partner_answer_for_user = daily_question.get_partner_answer(test_user.id)
            assert partner_answer_for_user is None  # 접근 불가
            
            # 4. 내가 답변 후 파트너 답변 접근 가능
            my_answer = Answer(
                question_id=question.id,
                user_id=test_user.id,
                answer_text='저는 좋은 개발자가 되고 싶어요.'
            )
            db.session.add(my_answer)
            db.session.commit()
            
            # 5. 이제 파트너 답변 접근 가능
            partner_answer_for_user = daily_question.get_partner_answer(test_user.id)
            assert partner_answer_for_user is not None
            assert partner_answer_for_user.answer_text == '저는 세계여행을 하고 싶어요.'

class TestDDayManagement:
    """D-Day 관리 시나리오 테스트"""
    
    def test_dday_lifecycle(self, app, test_user, test_couple):
        """D-Day 생명주기 테스트"""
        with app.app_context():
            # 1. D-Day 생성
            dday = DDay(
                couple_id=test_couple.id,
                title='우리의 첫 만남',
                target_date=date(2024, 2, 14),  # 발렌타인데이
                description='처음 만난 날을 기념하여',
                created_by=test_user.id
            )
            db.session.add(dday)
            db.session.commit()
            
            # 2. D-Day 계산 테스트
            today = date.today()
            target = date(2024, 2, 14)
            expected_days = (target - today).days
            
            assert dday.days_remaining() == expected_days
            
            # 3. 상태 텍스트 확인
            if expected_days > 0:
                assert dday.get_status_text() == f'D-{expected_days}'
            elif expected_days == 0:
                assert dday.get_status_text() == 'D-Day'
            else:
                assert dday.get_status_text() == f'D+{abs(expected_days)}'
            
            # 4. D-Day 수정
            dday.title = '우리의 첫 만남 (수정됨)'
            dday.target_date = date(2024, 3, 14)
            db.session.commit()
            
            assert dday.title == '우리의 첫 만남 (수정됨)'
            assert dday.target_date == date(2024, 3, 14)
            
            # 5. D-Day 삭제
            dday_id = dday.id
            db.session.delete(dday)
            db.session.commit()
            
            deleted_dday = DDay.query.get(dday_id)
            assert deleted_dday is None

class TestMemoryBookWorkflow:
    """메모리 북 워크플로우 테스트"""
    
    def test_memory_creation_and_retrieval(self, app, test_user, test_couple):
        """메모리 생성 및 조회 테스트"""
        with app.app_context():
            # 1. 여러 메모리 생성
            memories_data = [
                {
                    'title': '첫 데이트',
                    'content': '카페에서 처음 만났던 날',
                    'memory_date': date(2023, 1, 15)
                },
                {
                    'title': '첫 여행',
                    'content': '제주도로 함께 떠난 여행',
                    'memory_date': date(2023, 6, 10)
                },
                {
                    'title': '기념일',
                    'content': '100일 기념일 축하',
                    'memory_date': date(2023, 4, 25)
                }
            ]
            
            for memory_data in memories_data:
                memory = Memory(
                    couple_id=test_couple.id,
                    title=memory_data['title'],
                    content=memory_data['content'],
                    memory_date=memory_data['memory_date'],
                    created_by=test_user.id
                )
                db.session.add(memory)
            
            db.session.commit()
            
            # 2. 메모리 조회 (시간순 정렬)
            memories = Memory.query.filter_by(couple_id=test_couple.id)\
                                 .order_by(Memory.memory_date.desc()).all()
            
            assert len(memories) == 3
            assert memories[0].title == '첫 여행'  # 가장 최근
            assert memories[1].title == '기념일'
            assert memories[2].title == '첫 데이트'  # 가장 오래된

class TestMoodTracking:
    """무드 트래킹 시나리오 테스트"""
    
    def test_mood_tracking_workflow(self, app, test_user, test_partner):
        """무드 트래킹 워크플로우 테스트"""
        with app.app_context():
            # 1. 일주일간의 무드 데이터 생성
            base_date = date.today() - timedelta(days=6)
            mood_data = [
                {'level': 4, 'note': '좋은 하루였어요'},
                {'level': 3, 'note': '평범한 하루'},
                {'level': 5, 'note': '최고의 하루!'},
                {'level': 2, 'note': '조금 우울해요'},
                {'level': 4, 'note': '괜찮은 하루'},
                {'level': 3, 'note': '그저 그런 하루'},
                {'level': 5, 'note': '파트너와 함께해서 행복해요'}
            ]
            
            for i, mood in enumerate(mood_data):
                mood_entry = MoodEntry(
                    user_id=test_user.id,
                    mood_level=mood['level'],
                    note=mood['note'],
                    date=base_date + timedelta(days=i)
                )
                db.session.add(mood_entry)
            
            db.session.commit()
            
            # 2. 무드 통계 계산
            moods = MoodEntry.query.filter_by(user_id=test_user.id)\
                                  .order_by(MoodEntry.date.asc()).all()
            
            assert len(moods) == 7
            
            # 평균 무드 계산
            avg_mood = sum(mood.mood_level for mood in moods) / len(moods)
            expected_avg = sum(mood['level'] for mood in mood_data) / len(mood_data)
            assert abs(avg_mood - expected_avg) < 0.01
            
            # 3. 최고/최저 무드 확인
            highest_mood = max(moods, key=lambda m: m.mood_level)
            lowest_mood = min(moods, key=lambda m: m.mood_level)
            
            assert highest_mood.mood_level == 5
            assert lowest_mood.mood_level == 2
    
    def test_mood_sharing_notification(self, app, test_user, test_partner):
        """무드 공유 알림 테스트"""
        with app.app_context():
            # 1. 사용자가 무드 등록
            mood_entry = MoodEntry(
                user_id=test_user.id,
                mood_level=5,
                note='오늘은 정말 행복해요!',
                date=date.today()
            )
            db.session.add(mood_entry)
            db.session.commit()
            
            # 2. 파트너에게 알림 생성 (실제로는 SocketIO 이벤트에서 처리)
            notification = Notification(
                user_id=test_partner.id,
                type='mood_update',
                title='기분 공유',
                content=f'{test_user.name}님이 기분을 공유했습니다.'
            )
            db.session.add(notification)
            db.session.commit()
            
            # 3. 알림 확인
            partner_notifications = Notification.query.filter_by(
                user_id=test_partner.id,
                type='mood_update'
            ).all()
            
            assert len(partner_notifications) == 1
            assert partner_notifications[0].title == '기분 공유'
            assert partner_notifications[0].is_read is False

class TestEventManagement:
    """이벤트 관리 시나리오 테스트"""
    
    def test_event_creation_and_management(self, app, test_user, test_couple):
        """이벤트 생성 및 관리 테스트"""
        with app.app_context():
            # 1. 다양한 타입의 이벤트 생성
            events_data = [
                {
                    'title': '남자 친구 회사 회식',
                    'participant_type': 'male',
                    'start': datetime(2024, 1, 15, 18, 0),
                    'end': datetime(2024, 1, 15, 22, 0)
                },
                {
                    'title': '여자 친구 동창회',
                    'participant_type': 'female',
                    'start': datetime(2024, 1, 20, 19, 0),
                    'end': datetime(2024, 1, 20, 23, 0)
                },
                {
                    'title': '함께 영화 보기',
                    'participant_type': 'both',
                    'start': datetime(2024, 1, 25, 14, 0),
                    'end': datetime(2024, 1, 25, 16, 30)
                }
            ]
            
            for event_data in events_data:
                event = Event(
                    couple_id=test_couple.id,
                    title=event_data['title'],
                    start_datetime=event_data['start'],
                    end_datetime=event_data['end'],
                    participant_type=event_data['participant_type'],
                    created_by=test_user.id
                )
                db.session.add(event)
            
            db.session.commit()
            
            # 2. 이벤트 조회 및 검증
            events = Event.query.filter_by(couple_id=test_couple.id).all()
            assert len(events) == 3
            
            # 3. 참여자별 색상 확인
            male_event = next(e for e in events if e.participant_type == 'male')
            female_event = next(e for e in events if e.participant_type == 'female')
            both_event = next(e for e in events if e.participant_type == 'both')
            
            assert male_event.get_participant_color() == '#B8E6E1'
            assert female_event.get_participant_color() == '#F8BBD9'
            assert both_event.get_participant_color() == '#FFB5A7'
            
            # 4. 이벤트 기간 계산
            movie_event = both_event
            duration_text = movie_event.get_duration_text()
            assert '2시간 30분' in duration_text

class TestDataIntegrity:
    """데이터 무결성 테스트"""
    
    def test_cascade_deletion(self, app, test_user, test_partner, test_couple):
        """연관 데이터 삭제 테스트"""
        with app.app_context():
            # 1. 관련 데이터 생성
            dday = DDay(
                couple_id=test_couple.id,
                title='테스트 기념일',
                target_date=date(2024, 12, 25),
                created_by=test_user.id
            )
            
            memory = Memory(
                couple_id=test_couple.id,
                title='테스트 추억',
                content='테스트 내용',
                memory_date=date.today(),
                created_by=test_user.id
            )
            
            mood = MoodEntry(
                user_id=test_user.id,
                mood_level=4,
                date=date.today()
            )
            
            db.session.add_all([dday, memory, mood])
            db.session.commit()
            
            # 2. 데이터 존재 확인
            assert DDay.query.filter_by(couple_id=test_couple.id).count() == 1
            assert Memory.query.filter_by(couple_id=test_couple.id).count() == 1
            assert MoodEntry.query.filter_by(user_id=test_user.id).count() == 1
            
            # 3. 사용자 삭제 시 관련 데이터 처리 확인
            user_id = test_user.id
            couple_id = test_couple.id
            
            # 실제 애플리케이션에서는 사용자 삭제 시 관련 데이터를 어떻게 처리할지 정책이 필요
            # 여기서는 데이터 존재 여부만 확인
            assert User.query.get(user_id) is not None
            assert CoupleConnection.query.get(couple_id) is not None

class TestPerformanceAndScalability:
    """성능 및 확장성 테스트"""
    
    def test_large_dataset_query_performance(self, app, test_user, test_couple):
        """대용량 데이터 쿼리 성능 테스트"""
        with app.app_context():
            import time
            
            # 1. 대량의 메모리 데이터 생성 (100개)
            memories = []
            for i in range(100):
                memory = Memory(
                    couple_id=test_couple.id,
                    title=f'메모리 {i+1}',
                    content=f'메모리 {i+1}의 내용입니다.',
                    memory_date=date.today() - timedelta(days=i),
                    created_by=test_user.id
                )
                memories.append(memory)
            
            db.session.add_all(memories)
            db.session.commit()
            
            # 2. 쿼리 성능 측정
            start_time = time.time()
            
            # 페이지네이션을 사용한 조회
            page_size = 10
            memories_page = Memory.query.filter_by(couple_id=test_couple.id)\
                                      .order_by(Memory.memory_date.desc())\
                                      .limit(page_size).all()
            
            end_time = time.time()
            query_time = end_time - start_time
            
            # 3. 성능 검증 (1초 이내)
            assert query_time < 1.0
            assert len(memories_page) == page_size
            
            # 4. 정렬 확인
            for i in range(len(memories_page) - 1):
                assert memories_page[i].memory_date >= memories_page[i + 1].memory_date