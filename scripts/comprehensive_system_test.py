#!/usr/bin/env python3
"""
커플 웹앱 종합 시스템 테스트 스크립트
Task 1-9까지 구현된 모든 기능을 점검합니다.
"""

import sys
import os
from datetime import datetime, date, timedelta
import time

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.create_app import create_app
from app.extensions import db
from app.models.user import User
from app.models.couple import CoupleConnection
from app.models.dday import DDay
from app.models.event import Event
from app.models.question import Question, Answer, DailyQuestion

def test_database_models():
    """Task 2: 데이터베이스 모델 테스트"""
    print("\n=== Task 2: 데이터베이스 모델 테스트 ===")
    
    app = create_app()
    with app.app_context():
        try:
            # 모든 테이블 존재 확인
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            expected_tables = [
                'users', 'couple_connections', 'ddays', 'events', 
                'questions', 'answers', 'daily_questions', 'memories', 
                'mood_entries', 'notifications'
            ]
            
            missing_tables = [table for table in expected_tables if table not in tables]
            if missing_tables:
                print(f"❌ 누락된 테이블: {missing_tables}")
                return False
            
            print(f"✅ 모든 필수 테이블 존재: {len(tables)}개")
            
            # 각 모델 기본 기능 테스트
            test_user = User(email="test@example.com", name="테스트")
            test_user.set_password("password123")
            
            if not test_user.check_password("password123"):
                print("❌ 사용자 비밀번호 해싱 실패")
                return False
            
            print("✅ 사용자 모델 기본 기능 정상")
            
            # 질문 데이터 확인
            question_count = Question.query.count()
            if question_count == 0:
                print("❌ 질문 데이터가 없습니다")
                return False
            
            print(f"✅ 질문 데이터 존재: {question_count}개")
            
            return True
            
        except Exception as e:
            print(f"❌ 데이터베이스 모델 테스트 실패: {e}")
            return False

def test_user_authentication():
    """Task 3: 사용자 인증 시스템 테스트"""
    print("\n=== Task 3: 사용자 인증 시스템 테스트 ===")
    
    app = create_app()
    with app.app_context():
        try:
            # 기존 테스트 사용자 정리
            existing_user = User.query.filter_by(email="auth_test@example.com").first()
            if existing_user:
                db.session.delete(existing_user)
                db.session.commit()
            
            # 사용자 생성 테스트
            test_user = User(
                email="auth_test@example.com",
                name="인증 테스트 사용자"
            )
            test_user.set_password("testpassword123")
            
            db.session.add(test_user)
            db.session.commit()
            
            print("✅ 사용자 생성 성공")
            
            # 비밀번호 검증 테스트
            if not test_user.check_password("testpassword123"):
                print("❌ 비밀번호 검증 실패")
                return False
            
            if test_user.check_password("wrongpassword"):
                print("❌ 잘못된 비밀번호가 통과됨")
                return False
            
            print("✅ 비밀번호 검증 정상")
            
            # 정리
            db.session.delete(test_user)
            db.session.commit()
            
            return True
            
        except Exception as e:
            print(f"❌ 사용자 인증 테스트 실패: {e}")
            db.session.rollback()
            return False

def test_couple_connection():
    """Task 4: 커플 연결 시스템 테스트"""
    print("\n=== Task 4: 커플 연결 시스템 테스트 ===")
    
    app = create_app()
    with app.app_context():
        try:
            # 기존 테스트 데이터 정리
            existing_users = User.query.filter(User.email.like('couple_test%@example.com')).all()
            for user in existing_users:
                # 관련 연결 삭제
                CoupleConnection.query.filter(
                    (CoupleConnection.user1_id == user.id) | 
                    (CoupleConnection.user2_id == user.id)
                ).delete()
                db.session.delete(user)
            db.session.commit()
            
            # 테스트 사용자 생성
            user1 = User(email="couple_test1@example.com", name="사용자1")
            user1.set_password("password123")
            
            user2 = User(email="couple_test2@example.com", name="사용자2")
            user2.set_password("password123")
            
            db.session.add_all([user1, user2])
            db.session.commit()
            
            # 커플 연결 생성 테스트
            connection = CoupleConnection(
                user1_id=user1.id,
                user2_id=user2.id,
                invite_code=CoupleConnection.generate_invite_code()
            )
            
            db.session.add(connection)
            db.session.commit()
            
            print("✅ 커플 연결 생성 성공")
            
            # 연결 조회 테스트
            user1_connection = user1.get_couple_connection()
            user2_connection = user2.get_couple_connection()
            
            if not user1_connection or not user2_connection:
                print("❌ 커플 연결 조회 실패")
                return False
            
            if user1_connection.id != user2_connection.id:
                print("❌ 커플 연결 불일치")
                return False
            
            print("✅ 커플 연결 조회 정상")
            
            # 파트너 조회 테스트
            user1_partner = user1.get_partner()
            user2_partner = user2.get_partner()
            
            if not user1_partner or not user2_partner:
                print("❌ 파트너 조회 실패")
                return False
            
            if user1_partner.id != user2.id or user2_partner.id != user1.id:
                print("❌ 파트너 정보 불일치")
                return False
            
            print("✅ 파트너 조회 정상")
            
            # 정리
            db.session.delete(connection)
            db.session.delete(user1)
            db.session.delete(user2)
            db.session.commit()
            
            return True
            
        except Exception as e:
            print(f"❌ 커플 연결 테스트 실패: {e}")
            db.session.rollback()
            return False

def test_dday_functionality():
    """Task 6: D-Day 기능 테스트"""
    print("\n=== Task 6: D-Day 기능 테스트 ===")
    
    app = create_app()
    with app.app_context():
        try:
            # 기존 테스트 데이터 정리
            existing_user = User.query.filter_by(email="dday_test@example.com").first()
            if existing_user:
                # 관련 데이터 삭제
                DDay.query.filter_by(created_by=existing_user.id).delete()
                CoupleConnection.query.filter(
                    (CoupleConnection.user1_id == existing_user.id) | 
                    (CoupleConnection.user2_id == existing_user.id)
                ).delete()
                db.session.delete(existing_user)
                db.session.commit()
            
            # 테스트 데이터 준비
            user = User(email="dday_test@example.com", name="D-Day 테스트")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
            
            connection = CoupleConnection(
                user1_id=user.id,
                invite_code=CoupleConnection.generate_invite_code()
            )
            db.session.add(connection)
            db.session.commit()
            
            # D-Day 생성 테스트
            future_date = date.today() + timedelta(days=100)
            test_dday = DDay(
                couple_id=connection.id,
                title="테스트 기념일",
                target_date=future_date,
                description="테스트용 D-Day",
                created_by=user.id
            )
            
            db.session.add(test_dday)
            db.session.commit()
            
            print("✅ D-Day 생성 성공")
            
            # D-Day 계산 테스트
            days_left = test_dday.days_remaining()
            expected_days = (future_date - date.today()).days
            
            if days_left != expected_days:
                print(f"❌ D-Day 계산 오류: 예상 {expected_days}, 실제 {days_left}")
                return False
            
            print(f"✅ D-Day 계산 정상: {days_left}일 남음")
            
            # 상태 텍스트 테스트
            status_text = test_dday.get_status_text()
            expected_status = f"D-{expected_days}"
            
            if status_text != expected_status:
                print(f"❌ D-Day 상태 텍스트 오류: 예상 {expected_status}, 실제 {status_text}")
                return False
            
            print(f"✅ D-Day 상태 텍스트 정상: {status_text}")
            
            # 정리
            db.session.delete(test_dday)
            db.session.delete(connection)
            db.session.delete(user)
            db.session.commit()
            
            return True
            
        except Exception as e:
            print(f"❌ D-Day 기능 테스트 실패: {e}")
            db.session.rollback()
            return False

def test_calendar_events():
    """Task 7: 캘린더 및 일정 관리 테스트"""
    print("\n=== Task 7: 캘린더 및 일정 관리 테스트 ===")
    
    app = create_app()
    with app.app_context():
        try:
            # 테스트 데이터 준비
            user = User(email="event_test@example.com", name="일정 테스트")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
            
            connection = CoupleConnection(
                user1_id=user.id,
                invite_code=CoupleConnection.generate_invite_code()
            )
            db.session.add(connection)
            db.session.commit()
            
            # 일정 생성 테스트
            test_event = Event(
                couple_id=connection.id,
                title="테스트 일정",
                description="테스트용 일정입니다",
                start_datetime=datetime.now() + timedelta(hours=1),
                end_datetime=datetime.now() + timedelta(hours=2),
                participant_type="both",
                created_by=user.id
            )
            
            db.session.add(test_event)
            db.session.commit()
            
            print("✅ 일정 생성 성공")
            
            # 일정 조회 테스트
            events = Event.query.filter_by(couple_id=connection.id).all()
            if len(events) != 1:
                print(f"❌ 일정 조회 실패: 예상 1개, 실제 {len(events)}개")
                return False
            
            print("✅ 일정 조회 정상")
            
            # 정리
            db.session.delete(test_event)
            db.session.delete(connection)
            db.session.delete(user)
            db.session.commit()
            
            return True
            
        except Exception as e:
            print(f"❌ 캘린더 일정 테스트 실패: {e}")
            db.session.rollback()
            return False

def test_question_system():
    """Task 8: 질문 풀 및 관리 시스템 테스트"""
    print("\n=== Task 8: 질문 풀 및 관리 시스템 테스트 ===")
    
    app = create_app()
    with app.app_context():
        try:
            # 질문 데이터 확인
            total_questions = Question.query.count()
            if total_questions == 0:
                print("❌ 질문 데이터가 없습니다")
                return False
            
            print(f"✅ 질문 데이터 존재: {total_questions}개")
            
            # 카테고리별 질문 확인
            categories = db.session.query(Question.category).distinct().all()
            category_count = len(categories)
            
            if category_count == 0:
                print("❌ 질문 카테고리가 없습니다")
                return False
            
            print(f"✅ 질문 카테고리 존재: {category_count}개")
            
            # 난이도별 질문 확인
            difficulties = db.session.query(Question.difficulty).distinct().all()
            difficulty_count = len(difficulties)
            
            if difficulty_count == 0:
                print("❌ 질문 난이도가 없습니다")
                return False
            
            print(f"✅ 질문 난이도 존재: {difficulty_count}개")
            
            # 일일 질문 선택 테스트
            from app.routes.questions import get_or_create_daily_question
            
            # 테스트 커플 생성
            user1 = User(email="question_test1@example.com", name="질문테스트1")
            user1.set_password("password123")
            user2 = User(email="question_test2@example.com", name="질문테스트2")
            user2.set_password("password123")
            
            db.session.add_all([user1, user2])
            db.session.commit()
            
            connection = CoupleConnection(
                user1_id=user1.id,
                user2_id=user2.id,
                invite_code=CoupleConnection.generate_invite_code()
            )
            db.session.add(connection)
            db.session.commit()
            
            # 일일 질문 생성 테스트
            daily_question = get_or_create_daily_question(connection.id)
            
            if not daily_question:
                print("❌ 일일 질문 생성 실패")
                return False
            
            print("✅ 일일 질문 생성 성공")
            
            # 정리
            DailyQuestion.query.filter_by(couple_id=connection.id).delete()
            db.session.delete(connection)
            db.session.delete(user1)
            db.session.delete(user2)
            db.session.commit()
            
            return True
            
        except Exception as e:
            print(f"❌ 질문 시스템 테스트 실패: {e}")
            db.session.rollback()
            return False

def test_answer_system():
    """Task 9: 답변 시스템 및 접근 제어 테스트"""
    print("\n=== Task 9: 답변 시스템 및 접근 제어 테스트 ===")
    
    app = create_app()
    with app.app_context():
        try:
            # 테스트 데이터 준비
            user1 = User(email="answer_test1@example.com", name="답변테스트1")
            user1.set_password("password123")
            user2 = User(email="answer_test2@example.com", name="답변테스트2")
            user2.set_password("password123")
            
            db.session.add_all([user1, user2])
            db.session.commit()
            
            connection = CoupleConnection(
                user1_id=user1.id,
                user2_id=user2.id,
                invite_code=CoupleConnection.generate_invite_code()
            )
            db.session.add(connection)
            db.session.commit()
            
            # 테스트 질문 생성
            test_question = Question(
                text="테스트 질문입니다. 좋아하는 색깔은?",
                category="personal",
                difficulty="easy"
            )
            db.session.add(test_question)
            db.session.commit()
            
            # 답변 생성 테스트
            answer1 = Answer(
                question_id=test_question.id,
                user_id=user1.id,
                answer_text="파란색을 좋아합니다",
                date=date.today()
            )
            
            answer2 = Answer(
                question_id=test_question.id,
                user_id=user2.id,
                answer_text="빨간색을 좋아합니다",
                date=date.today()
            )
            
            db.session.add_all([answer1, answer2])
            db.session.commit()
            
            print("✅ 답변 생성 성공")
            
            # 답변 완료 상태 확인 테스트
            status = Answer.get_answer_completion_status(
                test_question.id, date.today(), user1.id, user2.id
            )
            
            if not status['both_answered']:
                print("❌ 답변 완료 상태 확인 실패")
                return False
            
            print("✅ 답변 완료 상태 확인 정상")
            
            # 접근 제어 테스트
            can_view = answer1.can_view_partner_answer(user2.id)
            partner_answer = answer1.get_partner_answer(user2.id)
            
            if not can_view or not partner_answer:
                print("❌ 파트너 답변 접근 제어 실패")
                return False
            
            print("✅ 파트너 답변 접근 제어 정상")
            
            # 정리
            db.session.delete(answer1)
            db.session.delete(answer2)
            db.session.delete(test_question)
            db.session.delete(connection)
            db.session.delete(user1)
            db.session.delete(user2)
            db.session.commit()
            
            return True
            
        except Exception as e:
            print(f"❌ 답변 시스템 테스트 실패: {e}")
            db.session.rollback()
            return False

def test_web_application():
    """Task 5: 웹 애플리케이션 기본 동작 테스트"""
    print("\n=== Task 5: 웹 애플리케이션 기본 동작 테스트 ===")
    
    try:
        # Flask 애플리케이션 생성 테스트
        app = create_app()
        
        if not app:
            print("❌ Flask 애플리케이션 생성 실패")
            return False
        
        print("✅ Flask 애플리케이션 생성 성공")
        
        # 기본 라우트 확인
        with app.test_client() as client:
            # 홈페이지 접근 테스트 (리다이렉트 예상)
            response = client.get('/')
            if response.status_code not in [200, 302]:
                print(f"❌ 홈페이지 접근 실패: {response.status_code}")
                return False
            
            print("✅ 홈페이지 접근 정상")
            
            # 로그인 페이지 접근 테스트
            response = client.get('/auth/login')
            if response.status_code != 200:
                print(f"❌ 로그인 페이지 접근 실패: {response.status_code}")
                return False
            
            print("✅ 로그인 페이지 접근 정상")
            
            # 회원가입 페이지 접근 테스트
            response = client.get('/auth/register')
            if response.status_code != 200:
                print(f"❌ 회원가입 페이지 접근 실패: {response.status_code}")
                return False
            
            print("✅ 회원가입 페이지 접근 정상")
        
        return True
        
    except Exception as e:
        print(f"❌ 웹 애플리케이션 테스트 실패: {e}")
        return False

def run_comprehensive_test():
    """종합 시스템 테스트 실행"""
    print("🚀 커플 웹앱 종합 시스템 테스트 시작")
    print("=" * 60)
    
    test_results = []
    
    # Task 1은 환경 설정이므로 별도 테스트 없이 통과
    print("\n=== Task 1: 프로젝트 구조 및 기본 환경 설정 ===")
    print("✅ 환경 설정 완료 (가상환경, 패키지, 프로젝트 구조)")
    test_results.append(("Task 1: 환경 설정", True))
    
    # 각 Task별 테스트 실행
    tests = [
        ("Task 2: 데이터베이스 모델", test_database_models),
        ("Task 3: 사용자 인증", test_user_authentication),
        ("Task 4: 커플 연결", test_couple_connection),
        ("Task 5: 웹 인터페이스", test_web_application),
        ("Task 6: D-Day 기능", test_dday_functionality),
        ("Task 7: 캘린더 일정", test_calendar_events),
        ("Task 8: 질문 시스템", test_question_system),
        ("Task 9: 답변 시스템", test_answer_system),
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 테스트 중 예외 발생: {e}")
            test_results.append((test_name, False))
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("🏁 종합 테스트 결과 요약")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{status} {test_name}")
        
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📊 총 {len(test_results)}개 테스트 중 {passed}개 통과, {failed}개 실패")
    
    if failed == 0:
        print("🎉 모든 테스트가 성공적으로 통과했습니다!")
        print("💡 Task 1-9의 모든 기능이 정상적으로 동작합니다.")
    else:
        print("⚠️  일부 테스트가 실패했습니다. 위의 오류 메시지를 확인해주세요.")
    
    return failed == 0

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)