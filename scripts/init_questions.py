#!/usr/bin/env python3
"""
질문 데이터베이스 초기화 스크립트
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.create_app import create_app
from app.extensions import db
from app.models.question import Question
from app.data.questions import QUESTIONS_DATA

def init_questions():
    """질문 데이터베이스 초기화"""
    app = create_app()
    
    with app.app_context():
        print("🔍 질문 데이터베이스 상태 확인 중...")
        
        # 질문 개수 확인
        question_count = Question.query.count()
        print(f"현재 데이터베이스의 질문 개수: {question_count}")
        
        if question_count == 0:
            print("📝 질문 데이터를 추가합니다...")
            
            for q_data in QUESTIONS_DATA:
                question = Question(
                    text=q_data['text'],
                    category=q_data['category'],
                    difficulty=q_data['difficulty']
                )
                db.session.add(question)
            
            try:
                db.session.commit()
                print(f"✅ {len(QUESTIONS_DATA)}개의 질문을 성공적으로 추가했습니다.")
            except Exception as e:
                db.session.rollback()
                print(f"❌ 질문 추가 중 오류 발생: {e}")
                return False
        else:
            print("✅ 질문 데이터가 이미 존재합니다.")
        
        # 카테고리별 질문 개수 확인
        print("\n📊 카테고리별 질문 개수:")
        from app.data.questions import CATEGORIES
        for category_key, category_info in CATEGORIES.items():
            count = Question.query.filter_by(category=category_key).count()
            print(f"  {category_info['emoji']} {category_info['name']}: {count}개")
        
        return True

if __name__ == "__main__":
    success = init_questions()
    sys.exit(0 if success else 1)