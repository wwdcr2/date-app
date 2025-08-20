#!/usr/bin/env python3
"""
로그인을 포함한 Questions API 테스트
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

def test_questions_with_login():
    """로그인을 포함한 Questions API 테스트"""
    app = create_app()
    
    with app.app_context():
        print("🧪 로그인 포함 Questions API 테스트")
        print("=" * 50)
        
        # 테스트 사용자 확인
        user1 = User.query.filter_by(email='test1@example.com').first()
        if not user1:
            print("❌ 테스트 사용자가 없습니다.")
            return False
        
        connection = user1.get_couple_connection()
        if not connection:
            print("❌ 커플 연결이 없습니다.")
            return False
        
        print(f"✅ 테스트 사용자: {user1.name} ({user1.email})")
        print(f"✅ 커플 연결 ID: {connection.id}")
        
        # Flask 테스트 클라이언트 사용
        with app.test_client() as client:
            # 1. 로그인 페이지 접근
            print("\n1️⃣ 로그인 페이지 접근")
            response = client.get('/auth/login')
            print(f"   - 상태 코드: {response.status_code}")
            
            if response.status_code != 200:
                print("❌ 로그인 페이지 접근 실패")
                return False
            
            # 2. 로그인 시도
            print("\n2️⃣ 로그인 시도")
            response = client.post('/auth/login', data={
                'email': 'test1@example.com',
                'password': 'password123'
            }, follow_redirects=False)
            
            print(f"   - 로그인 응답 상태 코드: {response.status_code}")
            
            if response.status_code == 302:
                print("   ✅ 로그인 성공 (리다이렉트)")
                location = response.headers.get('Location', '')
                print(f"   - 리다이렉트 위치: {location}")
            else:
                print(f"   ❌ 로그인 실패: {response.status_code}")
                print(f"   - 응답 내용: {response.get_data(as_text=True)[:200]}")
                return False
            
            # 3. 로그인 후 /questions/daily 접근
            print("\n3️⃣ /questions/daily 접근")
            response = client.get('/questions/daily')
            print(f"   - 상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ /questions/daily 접근 성공")
                content = response.get_data(as_text=True)
                print(f"   - 응답 크기: {len(content)} bytes")
                
                # HTML 내용 확인
                if "질문" in content or "question" in content:
                    print("   ✅ 질문 관련 내용 포함")
                else:
                    print("   ⚠️ 질문 관련 내용 없음")
                    
                # 오늘의 질문 텍스트 확인
                if "오늘의 질문" in content:
                    print("   ✅ '오늘의 질문' 텍스트 발견")
                    
            elif response.status_code == 302:
                location = response.headers.get('Location', '')
                print(f"   ⚠️ 리다이렉트됨: {location}")
                
                # 리다이렉트 따라가기
                if location.startswith('/'):
                    print("   🔄 리다이렉트 따라가기...")
                    response = client.get(location)
                    print(f"   - 최종 상태 코드: {response.status_code}")
                    
            else:
                print(f"   ❌ 접근 실패: {response.status_code}")
                content = response.get_data(as_text=True)
                print(f"   - 응답 내용 (처음 300자): {content[:300]}")
                return False
            
            # 4. API 엔드포인트 테스트
            print("\n4️⃣ /questions/api/daily-question API 테스트")
            response = client.get('/questions/api/daily-question')
            print(f"   - 상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.get_json()
                    print("   ✅ API 응답 성공")
                    print(f"   - Success: {data.get('success', 'Unknown')}")
                    
                    if data.get('success'):
                        question = data.get('question', {})
                        print(f"   - 질문 ID: {question.get('id', 'Unknown')}")
                        print(f"   - 질문 내용: {question.get('text', 'Unknown')[:50]}...")
                        print(f"   - 카테고리: {question.get('category', 'Unknown')}")
                        print(f"   - 난이도: {question.get('difficulty', 'Unknown')}")
                        
                        # 답변 상태 확인
                        my_answer = data.get('my_answer')
                        partner_answer = data.get('partner_answer')
                        print(f"   - 내 답변: {'있음' if my_answer else '없음'}")
                        print(f"   - 파트너 답변: {'있음' if partner_answer else '없음'}")
                        
                    else:
                        print(f"   - 오류 메시지: {data.get('message', 'Unknown')}")
                        
                except Exception as e:
                    print(f"   ❌ JSON 파싱 실패: {e}")
                    content = response.get_data(as_text=True)
                    print(f"   - 응답 내용: {content[:200]}")
                    
            else:
                print(f"   ❌ API 접근 실패: {response.status_code}")
                content = response.get_data(as_text=True)
                print(f"   - 응답 내용: {content[:200]}")
            
            # 5. 답변 제출 테스트
            print("\n5️⃣ 답변 제출 테스트")
            
            # 먼저 오늘의 질문 가져오기
            daily_question = DailyQuestion.query.filter_by(
                couple_id=connection.id,
                date=date.today()
            ).first()
            
            if daily_question:
                answer_data = {
                    'question_id': daily_question.question_id,
                    'answer': '테스트 답변입니다. 오늘은 정말 좋은 하루였어요!',
                    'date': date.today().isoformat()
                }
                
                response = client.post('/questions/answer', 
                                     json=answer_data,
                                     content_type='application/json')
                
                print(f"   - 답변 제출 상태 코드: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.get_json()
                        print(f"   ✅ 답변 제출 성공: {data.get('message', 'Unknown')}")
                        print(f"   - 업데이트 여부: {data.get('is_update', False)}")
                    except Exception as e:
                        print(f"   ❌ 응답 파싱 실패: {e}")
                else:
                    print(f"   ❌ 답변 제출 실패: {response.status_code}")
                    content = response.get_data(as_text=True)
                    print(f"   - 응답 내용: {content[:200]}")
            else:
                print("   ⚠️ 오늘의 일일 질문이 없어서 답변 테스트 생략")
        
        print("\n" + "=" * 50)
        print("🎉 로그인 포함 Questions API 테스트 완료!")
        return True

if __name__ == "__main__":
    success = test_questions_with_login()
    sys.exit(0 if success else 1)