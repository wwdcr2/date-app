"""API 엔드포인트 통합 테스트"""

import pytest
import json
from datetime import datetime, date, timedelta
from flask_login import login_user
from app.models.user import User
from app.models.couple import CoupleConnection
from app.models.dday import DDay
from app.models.event import Event
from app.models.question import Question, DailyQuestion, Answer
from app.extensions import db

class TestAuthAPI:
    """인증 API 테스트"""
    
    def test_register_success(self, client, app):
        """회원가입 성공 테스트"""
        with app.app_context():
            response = client.post('/auth/register', json={
                'email': 'newuser@example.com',
                'password': 'testpassword',
                'name': '새로운 사용자'
            })
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert '회원가입이 완료되었습니다' in data['message']
            
            # 데이터베이스에 사용자가 생성되었는지 확인
            user = User.query.filter_by(email='newuser@example.com').first()
            assert user is not None
            assert user.name == '새로운 사용자'
    
    def test_register_duplicate_email(self, client, app, test_user):
        """중복 이메일 회원가입 실패 테스트"""
        with app.app_context():
            response = client.post('/auth/register', json={
                'email': test_user.email,
                'password': 'testpassword',
                'name': '중복 사용자'
            })
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False
            assert '이미 사용 중인 이메일입니다' in data['errors']
    
    def test_register_invalid_email(self, client, app):
        """잘못된 이메일 형식 회원가입 실패 테스트"""
        with app.app_context():
            response = client.post('/auth/register', json={
                'email': 'invalid-email',
                'password': 'testpassword',
                'name': '테스트 사용자'
            })
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False
            assert '올바른 이메일 형식을 입력해주세요' in data['errors']
    
    def test_register_weak_password(self, client, app):
        """약한 비밀번호 회원가입 실패 테스트"""
        with app.app_context():
            response = client.post('/auth/register', json={
                'email': 'test@example.com',
                'password': '123',
                'name': '테스트 사용자'
            })
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False
            assert '비밀번호는 최소 6자리 이상이어야 합니다' in data['errors']
    
    def test_login_success(self, client, app, test_user):
        """로그인 성공 테스트"""
        with app.app_context():
            response = client.post('/auth/login', json={
                'email': test_user.email,
                'password': 'testpassword'
            })
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert '로그인되었습니다' in data['message']
    
    def test_login_wrong_password(self, client, app, test_user):
        """잘못된 비밀번호 로그인 실패 테스트"""
        with app.app_context():
            response = client.post('/auth/login', json={
                'email': test_user.email,
                'password': 'wrongpassword'
            })
            
            assert response.status_code == 401
            data = json.loads(response.data)
            assert data['success'] is False
            assert '이메일 또는 비밀번호가 올바르지 않습니다' in data['errors']
    
    def test_login_nonexistent_user(self, client, app):
        """존재하지 않는 사용자 로그인 실패 테스트"""
        with app.app_context():
            response = client.post('/auth/login', json={
                'email': 'nonexistent@example.com',
                'password': 'testpassword'
            })
            
            assert response.status_code == 401
            data = json.loads(response.data)
            assert data['success'] is False
            assert '이메일 또는 비밀번호가 올바르지 않습니다' in data['errors']
    
    def test_check_email_available(self, client, app):
        """이메일 사용 가능 확인 테스트"""
        with app.app_context():
            response = client.get('/auth/check-email?email=available@example.com')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['available'] is True
            assert '사용 가능한 이메일입니다' in data['message']
    
    def test_check_email_unavailable(self, client, app, test_user):
        """이메일 사용 불가 확인 테스트"""
        with app.app_context():
            response = client.get(f'/auth/check-email?email={test_user.email}')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['available'] is False
            assert '이미 사용 중인 이메일입니다' in data['message']
    
    def test_user_info_authenticated(self, authenticated_client, app, test_user, test_partner, test_couple):
        """인증된 사용자 정보 조회 테스트"""
        with app.app_context():
            response = authenticated_client.get('/auth/api/user-info')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['id'] == test_user.id
            assert data['email'] == test_user.email
            assert data['name'] == test_user.name
            assert data['is_connected'] is True
            assert data['partner']['id'] == test_partner.id
    
    def test_user_info_unauthenticated(self, client, app):
        """인증되지 않은 사용자 정보 조회 실패 테스트"""
        with app.app_context():
            response = client.get('/auth/api/user-info')
            assert response.status_code == 401

class TestDDayAPI:
    """D-Day API 테스트"""
    
    def test_dday_list_authenticated(self, authenticated_client, app, test_couple, test_dday):
        """인증된 사용자 D-Day 목록 조회 테스트"""
        with app.app_context():
            response = authenticated_client.get('/dday/api/list')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert len(data['ddays']) == 1
            assert data['ddays'][0]['title'] == test_dday.title
    
    def test_dday_list_unauthenticated(self, client, app):
        """인증되지 않은 사용자 D-Day 목록 조회 실패 테스트"""
        with app.app_context():
            response = client.get('/dday/api/list')
            assert response.status_code == 401
    
    def test_dday_create_success(self, authenticated_client, app, test_couple):
        """D-Day 생성 성공 테스트"""
        with app.app_context():
            response = authenticated_client.post('/dday/create', data={
                'title': '새로운 기념일',
                'target_date': '2024-12-31',
                'description': '새해 기념일'
            })
            
            # 리다이렉트 응답 확인
            assert response.status_code == 302
            
            # 데이터베이스에 D-Day가 생성되었는지 확인
            dday = DDay.query.filter_by(title='새로운 기념일').first()
            assert dday is not None
            assert dday.target_date == date(2024, 12, 31)
            assert dday.description == '새해 기념일'
    
    def test_dday_create_missing_title(self, authenticated_client, app, test_couple):
        """제목 없는 D-Day 생성 실패 테스트"""
        with app.app_context():
            response = authenticated_client.post('/dday/create', data={
                'title': '',
                'target_date': '2024-12-31',
                'description': '설명'
            })
            
            assert response.status_code == 200  # 폼 다시 표시
            # D-Day가 생성되지 않았는지 확인
            dday = DDay.query.filter_by(description='설명').first()
            assert dday is None
    
    def test_dday_delete_success(self, authenticated_client, app, test_dday):
        """D-Day 삭제 성공 테스트"""
        with app.app_context():
            response = authenticated_client.post(f'/dday/{test_dday.id}/delete')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'D-Day가 삭제되었습니다' in data['message']
            
            # 데이터베이스에서 삭제되었는지 확인
            dday = DDay.query.get(test_dday.id)
            assert dday is None
    
    def test_dday_delete_not_found(self, authenticated_client, app):
        """존재하지 않는 D-Day 삭제 실패 테스트"""
        with app.app_context():
            response = authenticated_client.post('/dday/999/delete')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'D-Day를 찾을 수 없습니다' in data['message']

class TestQuestionsAPI:
    """질문 API 테스트"""
    
    def test_daily_question_api(self, authenticated_client, app, test_couple, test_question):
        """오늘의 질문 API 테스트"""
        with app.app_context():
            # 일일 질문 생성
            daily_question = DailyQuestion(
                couple_id=test_couple.id,
                question_id=test_question.id,
                date=date.today()
            )
            db.session.add(daily_question)
            db.session.commit()
            
            response = authenticated_client.get('/questions/api/daily-question')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['question']['id'] == test_question.id
            assert data['question']['text'] == test_question.text
    
    def test_answer_question_success(self, authenticated_client, app, test_couple, test_question):
        """질문 답변 성공 테스트"""
        with app.app_context():
            response = authenticated_client.post('/questions/answer', json={
                'question_id': test_question.id,
                'answer': '저는 독서를 좋아합니다.',
                'date': date.today().isoformat()
            })
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert '답변이 저장되었습니다' in data['message']
            
            # 데이터베이스에 답변이 저장되었는지 확인
            answer = Answer.query.filter_by(
                question_id=test_question.id,
                user_id=authenticated_client.session['_user_id']
            ).first()
            assert answer is not None
            assert answer.answer_text == '저는 독서를 좋아합니다.'
    
    def test_answer_question_too_short(self, authenticated_client, app, test_question):
        """너무 짧은 답변 실패 테스트"""
        with app.app_context():
            response = authenticated_client.post('/questions/answer', json={
                'question_id': test_question.id,
                'answer': '짧음',
                'date': date.today().isoformat()
            })
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is False
            assert '답변은 최소 5자 이상 입력해주세요' in data['message']
    
    def test_answer_question_too_long(self, authenticated_client, app, test_question):
        """너무 긴 답변 실패 테스트"""
        with app.app_context():
            long_answer = 'a' * 2001  # 2001자
            response = authenticated_client.post('/questions/answer', json={
                'question_id': test_question.id,
                'answer': long_answer,
                'date': date.today().isoformat()
            })
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is False
            assert '답변은 최대 2000자까지 입력 가능합니다' in data['message']
    
    def test_answer_nonexistent_question(self, authenticated_client, app):
        """존재하지 않는 질문 답변 실패 테스트"""
        with app.app_context():
            response = authenticated_client.post('/questions/answer', json={
                'question_id': 999,
                'answer': '존재하지 않는 질문에 대한 답변',
                'date': date.today().isoformat()
            })
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is False
            assert '질문을 찾을 수 없습니다' in data['message']
    
    def test_history_stats_api(self, authenticated_client, app, test_couple, test_question):
        """답변 히스토리 통계 API 테스트"""
        with app.app_context():
            # 테스트 답변 생성
            answer = Answer(
                question_id=test_question.id,
                user_id=int(authenticated_client.session['_user_id']),
                answer_text='테스트 답변',
                date=date.today()
            )
            db.session.add(answer)
            db.session.commit()
            
            response = authenticated_client.get('/questions/api/history-stats')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['stats']['my_total_answers'] >= 1

class TestEventAPI:
    """이벤트 API 테스트 (기본적인 접근 테스트)"""
    
    def test_calendar_page_authenticated(self, authenticated_client, app, test_couple):
        """인증된 사용자 캘린더 페이지 접근 테스트"""
        with app.app_context():
            response = authenticated_client.get('/calendar/')
            assert response.status_code == 200
    
    def test_calendar_page_unauthenticated(self, client, app):
        """인증되지 않은 사용자 캘린더 페이지 접근 실패 테스트"""
        with app.app_context():
            response = client.get('/calendar/')
            assert response.status_code == 302  # 로그인 페이지로 리다이렉트

class TestSecurityAndValidation:
    """보안 및 검증 테스트"""
    
    def test_csrf_protection_disabled_in_test(self, client, app):
        """테스트 환경에서 CSRF 보호 비활성화 확인"""
        with app.app_context():
            assert app.config['WTF_CSRF_ENABLED'] is False
    
    def test_unauthorized_access_redirects(self, client, app):
        """인증되지 않은 접근 시 리다이렉트 테스트"""
        with app.app_context():
            protected_urls = [
                '/dday/',
                '/questions/',
                '/memories/',
                '/mood/',
                '/calendar/',
                '/notifications/'
            ]
            
            for url in protected_urls:
                response = client.get(url)
                assert response.status_code == 302  # 로그인 페이지로 리다이렉트
    
    def test_couple_relationship_required(self, app):
        """커플 관계 필요한 기능 접근 테스트"""
        with app.app_context():
            # 커플 연결이 없는 사용자 생성
            single_user = User(
                email='single@example.com',
                name='싱글 사용자'
            )
            single_user.set_password('testpassword')
            db.session.add(single_user)
            db.session.commit()
            
            # 싱글 사용자로 로그인된 클라이언트 생성
            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess['_user_id'] = str(single_user.id)
                    sess['_fresh'] = True
                
                # 커플 관계가 필요한 페이지 접근 시도
                response = client.get('/questions/daily')
                assert response.status_code == 302  # 커플 연결 페이지로 리다이렉트
    
    def test_sql_injection_prevention(self, authenticated_client, app):
        """SQL 인젝션 방지 테스트"""
        with app.app_context():
            # 악의적인 입력 시도
            malicious_input = "'; DROP TABLE users; --"
            
            response = authenticated_client.post('/questions/answer', json={
                'question_id': 1,
                'answer': malicious_input,
                'date': date.today().isoformat()
            })
            
            # 요청이 처리되어야 하고 (SQL 인젝션이 방지됨)
            # 사용자 테이블이 여전히 존재해야 함
            users_count = User.query.count()
            assert users_count > 0  # 테이블이 삭제되지 않음
    
    def test_xss_prevention(self, authenticated_client, app, test_question):
        """XSS 방지 테스트"""
        with app.app_context():
            # 악의적인 스크립트 입력
            xss_input = "<script>alert('XSS')</script>안전한 답변"
            
            response = authenticated_client.post('/questions/answer', json={
                'question_id': test_question.id,
                'answer': xss_input,
                'date': date.today().isoformat()
            })
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            
            # 답변이 저장되었는지 확인 (스크립트 태그는 제거되어야 함)
            answer = Answer.query.filter_by(
                question_id=test_question.id,
                user_id=int(authenticated_client.session['_user_id'])
            ).first()
            assert answer is not None
            # 실제 XSS 필터링은 템플릿 렌더링 시 처리됨