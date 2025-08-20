"""데이터베이스 초기화 유틸리티"""

from app.extensions import db
from app.models import *  # 모든 모델 import

def init_database():
    """데이터베이스 테이블 생성"""
    try:
        # 모든 테이블 생성
        db.create_all()
        print("✅ 데이터베이스 테이블이 성공적으로 생성되었습니다.")
        return True
    except Exception as e:
        print(f"❌ 데이터베이스 테이블 생성 중 오류 발생: {e}")
        return False

def drop_database():
    """모든 테이블 삭제 (주의: 모든 데이터가 삭제됩니다)"""
    try:
        db.drop_all()
        print("⚠️ 모든 데이터베이스 테이블이 삭제되었습니다.")
        return True
    except Exception as e:
        print(f"❌ 데이터베이스 테이블 삭제 중 오류 발생: {e}")
        return False

def reset_database():
    """데이터베이스 리셋 (삭제 후 재생성)"""
    print("🔄 데이터베이스를 리셋합니다...")
    if drop_database():
        return init_database()
    return False

def seed_questions():
    """초기 질문 데이터 삽입"""
    try:
        # 기존 질문이 있는지 확인
        if Question.query.count() > 0:
            print("ℹ️ 질문 데이터가 이미 존재합니다.")
            return True
        
        # 초기 질문 데이터
        initial_questions = [
            # 기본 질문들
            {"content": "오늘 가장 기뻤던 순간은 언제였나요?", "category": "daily", "difficulty_level": 1},
            {"content": "어린 시절 가장 좋아했던 놀이는 무엇인가요?", "category": "childhood", "difficulty_level": 1},
            {"content": "만약 하루 동안 투명인간이 될 수 있다면 무엇을 하고 싶나요?", "category": "imagination", "difficulty_level": 2},
            {"content": "가장 감동받았던 영화나 책은 무엇인가요?", "category": "culture", "difficulty_level": 1},
            {"content": "10년 후의 나는 어떤 모습일까요?", "category": "future", "difficulty_level": 2},
            
            # 관계 관련 질문들
            {"content": "우리가 처음 만났을 때의 첫인상은 어땠나요?", "category": "relationship", "difficulty_level": 2},
            {"content": "상대방의 어떤 점이 가장 매력적인가요?", "category": "relationship", "difficulty_level": 2},
            {"content": "함께 가고 싶은 여행지가 있다면 어디인가요?", "category": "relationship", "difficulty_level": 1},
            {"content": "우리 관계에서 가장 소중하게 생각하는 것은 무엇인가요?", "category": "relationship", "difficulty_level": 3},
            {"content": "상대방에게 고마운 점이 있다면 무엇인가요?", "category": "relationship", "difficulty_level": 2},
            
            # 깊은 질문들
            {"content": "인생에서 가장 중요하게 생각하는 가치는 무엇인가요?", "category": "values", "difficulty_level": 3},
            {"content": "가장 두려워하는 것은 무엇인가요?", "category": "deep", "difficulty_level": 3},
            {"content": "만약 시간을 되돌릴 수 있다면 언제로 돌아가고 싶나요?", "category": "deep", "difficulty_level": 3},
            {"content": "나를 가장 잘 표현하는 색깔은 무엇이고, 그 이유는 무엇인가요?", "category": "personality", "difficulty_level": 2},
            {"content": "스트레스를 받을 때 어떻게 해소하나요?", "category": "personality", "difficulty_level": 1},
            
            # 재미있는 질문들
            {"content": "만약 동물로 태어난다면 어떤 동물이 되고 싶나요?", "category": "fun", "difficulty_level": 1},
            {"content": "초능력을 하나 가질 수 있다면 무엇을 선택하겠나요?", "category": "fun", "difficulty_level": 1},
            {"content": "무인도에 하나만 가져갈 수 있다면 무엇을 가져가겠나요?", "category": "fun", "difficulty_level": 1},
            {"content": "만약 로또에 당첨된다면 가장 먼저 무엇을 하겠나요?", "category": "fun", "difficulty_level": 1},
            {"content": "어떤 유명인과 하루를 보내고 싶나요?", "category": "fun", "difficulty_level": 1},
            
            # 음식 관련
            {"content": "가장 좋아하는 음식과 그 이유는 무엇인가요?", "category": "food", "difficulty_level": 1},
            {"content": "함께 만들어보고 싶은 요리가 있나요?", "category": "food", "difficulty_level": 1},
            {"content": "어린 시절 엄마가 해주신 음식 중 가장 기억에 남는 것은?", "category": "food", "difficulty_level": 2},
            
            # 취미와 관심사
            {"content": "새로 배워보고 싶은 취미가 있나요?", "category": "hobby", "difficulty_level": 1},
            {"content": "가장 좋아하는 계절과 그 이유는 무엇인가요?", "category": "hobby", "difficulty_level": 1},
            {"content": "주말에 가장 하고 싶은 일은 무엇인가요?", "category": "hobby", "difficulty_level": 1},
        ]
        
        # 질문 데이터 삽입
        for q_data in initial_questions:
            question = Question(**q_data)
            db.session.add(question)
        
        db.session.commit()
        print(f"✅ {len(initial_questions)}개의 초기 질문이 성공적으로 추가되었습니다.")
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ 질문 데이터 삽입 중 오류 발생: {e}")
        return False

def seed_database():
    """초기 데이터 삽입"""
    print("🌱 초기 데이터를 삽입합니다...")
    success = True
    
    # 질문 데이터 삽입
    if not seed_questions():
        success = False
    
    if success:
        print("✅ 모든 초기 데이터가 성공적으로 삽입되었습니다.")
    else:
        print("❌ 일부 초기 데이터 삽입에 실패했습니다.")
    
    return success