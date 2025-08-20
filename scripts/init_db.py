#!/usr/bin/env python3
"""데이터베이스 초기화 스크립트"""

import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.create_app import create_app
from app.extensions import db

def init_database():
    """데이터베이스 초기화"""
    app = create_app()
    
    with app.app_context():
        # 모든 테이블 생성
        db.create_all()
        print("✅ 데이터베이스 테이블이 성공적으로 생성되었습니다!")
        
        # 테이블 목록 출력
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        print(f"\n📊 생성된 테이블 ({len(tables)}개):")
        for table in sorted(tables):
            print(f"  - {table}")

if __name__ == '__main__':
    init_database()