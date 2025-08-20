#!/usr/bin/env python3
"""
커플 웹앱 빠른 시스템 점검 스크립트
Task 1-9까지 구현된 핵심 기능만 간단히 점검합니다.
"""

import sys
import os
from datetime import datetime, date, timedelta

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.create_app import create_app
from app.extensions import db
from app.models.user import User
from app.models.couple import CoupleConnection
from app.models.dday import DDay
from app.models.event import Event
from app.models.question import Question, Answer, DailyQuestion

def quick_system_check():
    """빠른 시스템 점검"""
    print("🚀 커플 웹앱 빠른 시스템 점검")
    print("=" * 50)
    
    app = create_app()
    results = []
    
    with app.app_context():
        try:
            # 1. 데이터베이스 연결 확인
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            expected_tables = ['users', 'couple_connections', 'ddays', 'events', 'questions', 'answers']
            missing = [t for t in expected_tables if t not in tables]
            
            if not missing:
                results.append(("✅ 데이터베이스 테이블", "정상"))
            else:
                results.append(("❌ 데이터베이스 테이블", f"누락: {missing}"))
            
            # 2. 모델 기본 기능 확인
            try:
                test_user = User(email="quick_test@example.com", name="테스트")
                test_user.set_password("test123")
                if test_user.check_password("test123"):
                    results.append(("✅ 사용자 모델", "정상"))
                else:
                    results.append(("❌ 사용자 모델", "비밀번호 해싱 실패"))
            except Exception as e:
                results.append(("❌ 사용자 모델", str(e)))
            
            # 3. 질문 데이터 확인
            question_count = Question.query.count()
            if question_count > 0:
                results.append(("✅ 질문 데이터", f"{question_count}개"))
            else:
                results.append(("❌ 질문 데이터", "없음"))
            
            # 4. Flask 애플리케이션 확인
            with app.test_client() as client:
                response = client.get('/auth/login')
                if response.status_code == 200:
                    results.append(("✅ 웹 애플리케이션", "정상"))
                else:
                    results.append(("❌ 웹 애플리케이션", f"상태코드: {response.status_code}"))
            
            # 5. D-Day 모델 확인
            try:
                future_date = date.today() + timedelta(days=30)
                test_dday = DDay(
                    couple_id=1,
                    title="테스트",
                    target_date=future_date,
                    created_by=1
                )
                days = test_dday.days_remaining()
                status = test_dday.get_status_text()
                if days == 30 and status == "D-30":
                    results.append(("✅ D-Day 기능", "정상"))
                else:
                    results.append(("❌ D-Day 기능", f"계산 오류: {days}일, {status}"))
            except Exception as e:
                results.append(("❌ D-Day 기능", str(e)))
            
            # 6. 답변 모델 확인
            try:
                status = Answer.get_answer_completion_status(1, date.today(), 1, 2)
                if isinstance(status, dict) and 'both_answered' in status:
                    results.append(("✅ 답변 시스템", "정상"))
                else:
                    results.append(("❌ 답변 시스템", "상태 확인 실패"))
            except Exception as e:
                results.append(("❌ 답변 시스템", str(e)))
            
        except Exception as e:
            results.append(("❌ 전체 시스템", str(e)))
    
    # 결과 출력
    print("\n📊 점검 결과:")
    print("-" * 50)
    
    passed = 0
    failed = 0
    
    for status, message in results:
        print(f"{status}: {message}")
        if status.startswith("✅"):
            passed += 1
        else:
            failed += 1
    
    print(f"\n총 {len(results)}개 항목 중 {passed}개 통과, {failed}개 실패")
    
    if failed == 0:
        print("🎉 모든 핵심 기능이 정상 작동합니다!")
    else:
        print("⚠️  일부 기능에 문제가 있습니다.")
    
    return failed == 0

if __name__ == "__main__":
    success = quick_system_check()
    sys.exit(0 if success else 1)