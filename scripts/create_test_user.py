#!/usr/bin/env python3
"""
테스트용 사용자 생성 스크립트
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.create_app import create_app
from app.extensions import db
from app.models.user import User
from app.models.couple import CoupleConnection

def create_test_users():
    """테스트용 사용자 및 커플 생성"""
    app = create_app()
    
    with app.app_context():
        print("👥 테스트 사용자 생성 중...")
        
        # 기존 테스트 사용자 삭제
        User.query.filter(User.email.like('%test%')).delete()
        db.session.commit()
        
        # 테스트 사용자 1 생성
        user1 = User(
            email='test1@example.com',
            name='김철수'
        )
        user1.set_password('password123')
        db.session.add(user1)
        
        # 테스트 사용자 2 생성
        user2 = User(
            email='test2@example.com',
            name='이영희'
        )
        user2.set_password('password123')
        db.session.add(user2)
        
        db.session.commit()
        
        # 커플 연결 생성
        connection = CoupleConnection(
            user1_id=user1.id,
            user2_id=user2.id,
            invite_code=CoupleConnection.generate_invite_code()
        )
        db.session.add(connection)
        db.session.commit()
        
        print("✅ 테스트 사용자 생성 완료!")
        print(f"   - 사용자 1: {user1.email} / password123")
        print(f"   - 사용자 2: {user2.email} / password123")
        print(f"   - 커플 연결 ID: {connection.id}")
        print(f"   - 초대 코드: {connection.invite_code}")
        
        print("\n🔗 테스트 방법:")
        print("1. 서버 실행: python scripts/run_test_server.py")
        print("2. 브라우저에서 http://127.0.0.1:5003 접속")
        print("3. test1@example.com / password123 으로 로그인")
        print("4. http://127.0.0.1:5003/questions/daily 접속 테스트")

if __name__ == "__main__":
    create_test_users()