#!/usr/bin/env python3
"""
Questions API 테스트 스크립트
"""

import sys
import os
from datetime import date

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.create_app import create_app
from app.extensions import db
from app.models.user import User
from app.models.couple import CoupleConnection
from app.models.question import Question, DailyQuestion

def test_questions_api():
    """Questions API 테스트"""
    app = create_app()
    
    with app.app_context():
        print("🧪 Questions API 테스트 시작")
        print("=" * 50)
        
        # 테스트용 사용자 및 커플 생성
        user1 = User.query.filter_by(email='test1@example.com').first()
        user2 = User.query.filter_by(email='test2@example.com').first()
        
        if not user1:
            user1 = User(email='test1@example.com', name='테스트 사용자1')
            user1.set_password('password123')
            db.session.add(user1)
        
        if not user2:
            user2 = User(email='test2@example.com', name='테스트 사용자2')
            user2.set_password('password123')
            db.session.add(user2)
        
        db.session.commit()
        
        # 커플 연결
        connection = CoupleConnection.query.filter(
            ((CoupleConnection.user1_id == user1.id) & (CoupleConnection.user2_id == user2.id)) |
            ((CoupleConnection.user1_id == user2.id) & (CoupleConnection.user2_id == user1.id))
        ).first()
        
        if not connection:
            connection = CoupleConnection(
                user1_id=user1.id,
                user2_id=user2.id,
                invite_code=CoupleConnection.generate_invite_code()
            )
            db.session.add(connection)
            db.session.commit()
        
        print(f"✅ 테스트 커플 생성: {user1.name} ↔ {user2.name}")
        
        # 1. 질문 데이터 확인
        print("\n1️⃣ 질문 데이터 확인")
        question_count = Question.query.count()
        print(f"✅ 총 질문 개수: {question_count}")
        
        if question_count == 0:
            print("❌ 질문 데이터가 없습니다!")
            return False
        
        # 2. 일일 질문 생성 테스트
        print("\n2️⃣ 일일 질문 생성 테스트")
        from app.routes.questions import get_or_create_daily_question
        
        daily_question = get_or_create_daily_question(connection.id)
        
        if daily_question:
            print(f"✅ 일일 질문 생성 성공")
            print(f"   - 질문 ID: {daily_question.question_id}")
            print(f"   - 질문 내용: {daily_question.question.text}")
            print(f"   - 카테고리: {daily_question.question.category}")
            print(f"   - 난이도: {daily_question.question.difficulty}")
            print(f"   - 날짜: {daily_question.date}")
        else:
            print("❌ 일일 질문 생성 실패")
            return False
        
        # 3. 일일 질문 중복 생성 방지 테스트
        print("\n3️⃣ 일일 질문 중복 생성 방지 테스트")
        daily_question2 = get_or_create_daily_question(connection.id)
        
        if daily_question.id == daily_question2.id:
            print("✅ 중복 생성 방지 정상 (같은 일일 질문 반환)")
        else:
            print("❌ 중복 생성 방지 실패")
            return False
        
        # 4. 답변 상태 확인 테스트
        print("\n4️⃣ 답변 상태 확인 테스트")
        answer_status = daily_question.get_answer_status()
        
        print(f"✅ 답변 상태 확인:")
        print(f"   - user1 답변 여부: {answer_status['user1_answered']}")
        print(f"   - user2 답변 여부: {answer_status['user2_answered']}")
        print(f"   - 둘 다 답변 여부: {answer_status['both_answered']}")
        
        # 5. Flask 테스트 클라이언트로 API 테스트
        print("\n5️⃣ Flask 테스트 클라이언트로 API 테스트")
        
        with app.test_client() as client:
            # 로그인 없이 접근 시도
            response = client.get('/questions/daily')
            if response.status_code == 302:  # 리다이렉트 (로그인 필요)
                print("✅ 로그인 없이 접근 시 리다이렉트 정상")
            else:
                print(f"❌ 로그인 없이 접근 시 예상과 다른 응답: {response.status_code}")
            
            # 로그인 시뮬레이션 (세션 설정)
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user1.id)
                sess['_fresh'] = True
            
            # 로그인 후 접근
            response = client.get('/questions/daily')
            if response.status_code == 200:
                print("✅ 로그인 후 /questions/daily 접근 성공")
                print(f"   - 응답 크기: {len(response.data)} bytes")
            else:
                print(f"❌ 로그인 후 접근 실패: {response.status_code}")
                print(f"   - 응답 내용: {response.data.decode()[:200]}...")
                return False
            
            # API 엔드포인트 테스트
            response = client.get('/questions/api/daily-question')
            if response.status_code == 200:
                print("✅ /questions/api/daily-question API 접근 성공")
                data = response.get_json()
                if data and data.get('success'):
                    print(f"   - API 응답 성공")
                    print(f"   - 질문 텍스트: {data['question']['text'][:50]}...")
                else:
                    print(f"❌ API 응답 실패: {data}")
                    return False
            else:
                print(f"❌ API 접근 실패: {response.status_code}")
                return False
        
        # 테스트 데이터 정리
        print("\n🧹 테스트 데이터 정리")
        try:
            DailyQuestion.query.filter_by(couple_id=connection.id).delete()
            db.session.commit()
            print("✅ 테스트 일일 질문 정리 완료")
        except Exception as e:
            print(f"⚠️ 테스트 데이터 정리 중 오류: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 Questions API 테스트 완료!")
        
        return True

if __name__ == "__main__":
    success = test_questions_api()
    sys.exit(0 if success else 1)