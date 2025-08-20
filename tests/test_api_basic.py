"""기본 API 테스트"""

import pytest
import json
from datetime import date
from app.models.user import User
from app.models.couple import CoupleConnection
from app.models.dday import DDay
from app.extensions import db

class TestAuthAPI:
    """인증 API 기본 테스트"""
    
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
            
            # 데이터베이스에 사용자가 생성되었는지 확인
            user = User.query.filter_by(email='newuser@example.com').first()
            assert user is not None
            assert user.name == '새로운 사용자'
    
    def test_register_duplicate_email(self, client, app):
        """중복 이메일 회원가입 실패 테스트"""
        with app.app_context():
            # 첫 번째 사용자 생성
            user = User(email='duplicate@example.com', name='첫 번째 사용자')
            user.set_password('testpassword')
            db.session.add(user)
            db.session.commit()
            
            # 같은 이메일로 두 번째 사용자 생성 시도
            response = client.post('/auth/register', json={
                'email': 'duplicate@example.com',
                'password': 'testpassword',
                'name': '두 번째 사용자'
            })
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False
            assert '이미 사용 중인 이메일입니다' in data['errors']
    
    def test_login_success(self, client, app):
        """로그인 성공 테스트"""
        with app.app_context():
            # 테스트 사용자 생성
            user = User(email='login@example.com', name='로그인 테스트')
            user.set_password('testpassword')
            db.session.add(user)
            db.session.commit()
            
            response = client.post('/auth/login', json={
                'email': 'login@example.com',
                'password': 'testpassword'
            })
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert '로그인되었습니다' in data['message']
    
    def test_login_wrong_password(self, client, app):
        """잘못된 비밀번호 로그인 실패 테스트"""
        with app.app_context():
            # 테스트 사용자 생성
            user = User(email='wrongpw@example.com', name='비밀번호 테스트')
            user.set_password('correctpassword')
            db.session.add(user)
            db.session.commit()
            
            response = client.post('/auth/login', json={
                'email': 'wrongpw@example.com',
                'password': 'wrongpassword'
            })
            
            assert response.status_code == 401
            data = json.loads(response.data)
            assert data['success'] is False
            assert '이메일 또는 비밀번호가 올바르지 않습니다' in data['errors']

class TestDDayAPI:
    """D-Day API 기본 테스트"""
    
    def test_dday_list_unauthenticated(self, client, app):
        """인증되지 않은 사용자 D-Day 목록 조회 실패 테스트"""
        with app.app_context():
            response = client.get('/dday/api/list')
            assert response.status_code == 401
    
    def test_dday_create_form_success(self, client, app):
        """D-Day 폼 생성 성공 테스트 (인증된 사용자)"""
        with app.app_context():
            # 테스트 사용자 및 커플 생성
            user = User(email='dday@example.com', name='D-Day 테스트')
            user.set_password('testpassword')
            db.session.add(user)
            db.session.commit()
            
            connection = CoupleConnection(
                user1_id=user.id,
                user2_id=user.id,  # 테스트용
                invite_code='DDAY01'
            )
            db.session.add(connection)
            db.session.commit()
            
            # 로그인 상태 시뮬레이션
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True
            
            response = client.post('/dday/create', data={
                'title': '새로운 기념일',
                'target_date': '2024-12-31',
                'description': '새해 기념일'
            })
            
            # 리다이렉트 응답 확인 (성공 시 302)
            assert response.status_code == 302
            
            # 데이터베이스에 D-Day가 생성되었는지 확인
            dday = DDay.query.filter_by(title='새로운 기념일').first()
            assert dday is not None
            assert dday.target_date == date(2024, 12, 31)

class TestSecurityBasic:
    """기본 보안 테스트"""
    
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
    
    def test_csrf_protection_disabled_in_test(self, app):
        """테스트 환경에서 CSRF 보호 비활성화 확인"""
        with app.app_context():
            assert app.config['WTF_CSRF_ENABLED'] is False

class TestApplicationBasic:
    """애플리케이션 기본 테스트"""
    
    def test_app_creation(self, app):
        """애플리케이션 생성 테스트"""
        assert app is not None
        assert app.config['TESTING'] is True
    
    def test_database_connection(self, app):
        """데이터베이스 연결 테스트"""
        with app.app_context():
            # 간단한 쿼리 실행으로 연결 확인
            result = db.session.execute(db.text('SELECT 1')).scalar()
            assert result == 1
    
    def test_main_routes_accessible(self, client, app):
        """메인 라우트 접근 가능성 테스트"""
        with app.app_context():
            # 인증이 필요하지 않은 라우트들
            public_routes = [
                '/',
                '/auth/login',
                '/auth/register'
            ]
            
            for route in public_routes:
                response = client.get(route)
                # 200 (성공) 또는 302 (리다이렉트) 모두 정상
                assert response.status_code in [200, 302]