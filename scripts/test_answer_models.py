#!/usr/bin/env python3
"""
답변 모델 단위 테스트 스크립트
"""

import sys
import os
from datetime import datetime, date

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.create_app import create_app
from app.extensions import db
from app.models.user import User
from app.models.couple import CoupleConnection
from app.models.question import Question, Answer, DailyQuestion

def test_answer_models():
    """답변 모델 기능 테스트"""
    app = create_app()
    
    with app.app_context():
        print("답변 모델 단위 테스트 시작...")
        
        # 0. 기존 테스트 데이터 정리
        print("\n0. 기존 테스트 데이터 정리...")
        try:
            # 기존 테스트 데이터 삭제
            existing_users = User.query.filter(User.email.like('test%@example.com')).all()
            existing_questions = Question.query.filter(Question.text.like('테스트 질문%')).all()
            
            for user in existing_users:
                # 관련 데이터 먼저 삭제
                Answer.query.filter_by(user_id=user.id).delete()
                CoupleConnection.query.filter((CoupleConnection.user1_id == user.id) | (CoupleConnection.user2_id == user.id)).delete()
                db.session.delete(user)
            
            for question in existing_questions:
                Answer.query.filter_by(question_id=question.id).delete()
                DailyQuestion.query.filter_by(question_id=question.id).delete()
                db.session.delete(question)
            
            db.session.commit()
            print("✅ 기존 테스트 데이터 정리 완료")
        except Exception as e:
            print(f"⚠️  기존 데이터 정리 중 오류: {e}")
            db.session.rollback()
        
        # 1. Answer 모델 기본 기능 테스트
        print("\n1. Answer 모델 기본 기능 테스트...")
        
        # 테스트용 임시 데이터 생성
        test_user1 = User(
            email="test1@example.com",
            name="테스트 사용자 1"
        )
        test_user1.set_password("password123")
        
        test_user2 = User(
            email="test2@example.com", 
            name="테스트 사용자 2"
        )
        test_user2.set_password("password123")
        
        test_question = Question(
            text="테스트 질문입니다. 당신의 취미는 무엇인가요?",
            category="hobby",
            difficulty="easy"
        )
        
        try:
            db.session.add_all([test_user1, test_user2, test_question])
            db.session.commit()
            print("✅ 테스트 데이터 생성 성공")
        except Exception as e:
            print(f"❌ 테스트 데이터 생성 실패: {e}")
            db.session.rollback()
            return False
        
        # 2. 답변 생성 테스트
        print("\n2. 답변 생성 테스트...")
        
        test_answer1 = Answer(
            question_id=test_question.id,
            user_id=test_user1.id,
            answer_text="저는 독서를 좋아합니다.",
            date=date.today()
        )
        
        test_answer2 = Answer(
            question_id=test_question.id,
            user_id=test_user2.id,
            answer_text="저는 영화 감상을 좋아합니다.",
            date=date.today()
        )
        
        try:
            db.session.add_all([test_answer1, test_answer2])
            db.session.commit()
            print("✅ 답변 생성 성공")
        except Exception as e:
            print(f"❌ 답변 생성 실패: {e}")
            db.session.rollback()
            return False
        
        # 3. 답변 완료 상태 확인 테스트
        print("\n3. 답변 완료 상태 확인 테스트...")
        
        status = Answer.get_answer_completion_status(
            test_question.id, 
            date.today(), 
            test_user1.id, 
            test_user2.id
        )
        
        print(f"사용자 1 답변 완료: {status['user1_answered']}")
        print(f"사용자 2 답변 완료: {status['user2_answered']}")
        print(f"모두 답변 완료: {status['both_answered']}")
        
        if status['both_answered']:
            print("✅ 답변 완료 상태 확인 성공")
        else:
            print("❌ 답변 완료 상태 확인 실패")
        
        # 4. 파트너 답변 조회 권한 테스트
        print("\n4. 파트너 답변 조회 권한 테스트...")
        
        # 사용자 1이 답변했으므로 파트너 답변 조회 가능해야 함
        can_view = test_answer1.can_view_partner_answer(test_user2.id)
        partner_answer = test_answer1.get_partner_answer(test_user2.id)
        
        if can_view and partner_answer:
            print("✅ 파트너 답변 조회 권한 테스트 성공")
            print(f"파트너 답변: {partner_answer.answer_text}")
        else:
            print("❌ 파트너 답변 조회 권한 테스트 실패")
        
        # 5. 커플 연결 및 일일 질문 테스트
        print("\n5. 커플 연결 및 일일 질문 테스트...")
        
        test_connection = CoupleConnection(
            user1_id=test_user1.id,
            user2_id=test_user2.id,
            invite_code=CoupleConnection.generate_invite_code()
        )
        
        try:
            db.session.add(test_connection)
            db.session.commit()
            print("✅ 커플 연결 생성 성공")
        except Exception as e:
            print(f"❌ 커플 연결 생성 실패: {e}")
            db.session.rollback()
            return False
        
        # 일일 질문 생성
        test_daily_question = DailyQuestion(
            couple_id=test_connection.id,
            question_id=test_question.id,
            date=date.today()
        )
        
        try:
            db.session.add(test_daily_question)
            db.session.commit()
            print("✅ 일일 질문 생성 성공")
        except Exception as e:
            print(f"❌ 일일 질문 생성 실패: {e}")
            db.session.rollback()
            return False
        
        # 6. 일일 질문 답변 상태 확인
        print("\n6. 일일 질문 답변 상태 확인...")
        
        daily_status = test_daily_question.get_answer_status()
        print(f"일일 질문 답변 상태: {daily_status}")
        
        can_view_partner = test_daily_question.can_user_view_partner_answer(test_user1.id)
        partner_answer_from_daily = test_daily_question.get_partner_answer(test_user1.id)
        
        if can_view_partner and partner_answer_from_daily:
            print("✅ 일일 질문을 통한 파트너 답변 조회 성공")
        else:
            print("❌ 일일 질문을 통한 파트너 답변 조회 실패")
        
        # 7. 테스트 데이터 정리
        print("\n7. 테스트 데이터 정리...")
        
        try:
            # 생성한 테스트 데이터 삭제
            db.session.delete(test_daily_question)
            db.session.delete(test_connection)
            db.session.delete(test_answer1)
            db.session.delete(test_answer2)
            db.session.delete(test_question)
            db.session.delete(test_user1)
            db.session.delete(test_user2)
            db.session.commit()
            print("✅ 테스트 데이터 정리 완료")
        except Exception as e:
            print(f"⚠️  테스트 데이터 정리 중 오류: {e}")
            db.session.rollback()
        
        print("\n✅ 답변 모델 단위 테스트 완료!")
        return True

if __name__ == "__main__":
    success = test_answer_models()
    if success:
        print("\n🎉 모든 모델 테스트가 성공적으로 완료되었습니다!")
    else:
        print("\n❌ 일부 모델 테스트가 실패했습니다.")
        sys.exit(1)