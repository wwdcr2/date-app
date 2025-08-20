#!/usr/bin/env python3
"""
Questions API 디버깅 스크립트
"""

import sys
import os
import requests
from datetime import date

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_questions_api_with_requests():
    """requests를 사용한 실제 API 테스트"""
    base_url = "http://127.0.0.1:5003"
    
    print("🔍 Questions API 디버깅 시작")
    print("=" * 50)
    
    # 세션 생성
    session = requests.Session()
    
    try:
        # 1. 메인 페이지 접근 테스트
        print("1️⃣ 메인 페이지 접근 테스트")
        response = session.get(f"{base_url}/")
        print(f"   - 상태 코드: {response.status_code}")
        print(f"   - 응답 크기: {len(response.content)} bytes")
        
        # 2. 로그인 페이지 접근 테스트
        print("\n2️⃣ 로그인 페이지 접근 테스트")
        response = session.get(f"{base_url}/auth/login")
        print(f"   - 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ 로그인 페이지 정상 접근")
            
            # CSRF 토큰 추출 (간단한 방법)
            csrf_token = None
            if 'csrf_token' in response.text:
                # 실제 구현에서는 BeautifulSoup 등을 사용해야 하지만, 간단히 테스트
                print("   - CSRF 토큰 발견")
            
            # 3. 로그인 시도
            print("\n3️⃣ 로그인 시도")
            login_data = {
                'email': 'test1@example.com',
                'password': 'password123'
            }
            
            response = session.post(f"{base_url}/auth/login", data=login_data)
            print(f"   - 로그인 응답 상태 코드: {response.status_code}")
            
            if response.status_code == 302:
                print("   ✅ 로그인 성공 (리다이렉트)")
                
                # 4. 로그인 후 questions/daily 접근
                print("\n4️⃣ 로그인 후 /questions/daily 접근")
                response = session.get(f"{base_url}/questions/daily")
                print(f"   - 상태 코드: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ /questions/daily 접근 성공")
                    print(f"   - 응답 크기: {len(response.content)} bytes")
                    
                    # HTML에서 질문 내용 확인
                    if "질문" in response.text or "question" in response.text:
                        print("   ✅ 질문 내용 포함됨")
                    else:
                        print("   ⚠️ 질문 내용이 보이지 않음")
                        
                elif response.status_code == 302:
                    print(f"   ⚠️ 리다이렉트됨: {response.headers.get('Location', 'Unknown')}")
                else:
                    print(f"   ❌ 접근 실패: {response.status_code}")
                    print(f"   - 응답 내용 (처음 200자): {response.text[:200]}")
                
                # 5. API 엔드포인트 테스트
                print("\n5️⃣ /questions/api/daily-question API 테스트")
                response = session.get(f"{base_url}/questions/api/daily-question")
                print(f"   - 상태 코드: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print("   ✅ API 응답 성공")
                        print(f"   - Success: {data.get('success', 'Unknown')}")
                        if data.get('success'):
                            question = data.get('question', {})
                            print(f"   - 질문 ID: {question.get('id', 'Unknown')}")
                            print(f"   - 질문 내용: {question.get('text', 'Unknown')[:50]}...")
                            print(f"   - 카테고리: {question.get('category', 'Unknown')}")
                        else:
                            print(f"   - 오류 메시지: {data.get('message', 'Unknown')}")
                    except Exception as e:
                        print(f"   ❌ JSON 파싱 실패: {e}")
                        print(f"   - 응답 내용: {response.text[:200]}")
                else:
                    print(f"   ❌ API 접근 실패: {response.status_code}")
                    print(f"   - 응답 내용: {response.text[:200]}")
                    
            else:
                print(f"   ❌ 로그인 실패: {response.status_code}")
                print(f"   - 응답 내용 (처음 200자): {response.text[:200]}")
        else:
            print(f"   ❌ 로그인 페이지 접근 실패: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다.")
        print("   서버가 실행 중인지 확인해주세요: python scripts/run_test_server.py")
        return False
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎯 디버깅 완료")
    return True

if __name__ == "__main__":
    test_questions_api_with_requests()