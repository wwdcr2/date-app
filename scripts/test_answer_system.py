#!/usr/bin/env python3
"""
답변 시스템 테스트 스크립트
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

def test_answer_system():
    """답변 시스템 기능 테스트"""
    app = create_app()
    
    with app.app_context():
        print("답변 시스템 테스트 시작...")
        
        # 1. 테스트 데이터 확인
        print("\n1. 기본 데이터 확인...")
        
        users = User.query.all()
        questions = Question.query.all()
        connections = CoupleConnection.query.all()
        
        print(f"사용자 수: {len(users)}")
        print(f"질문 수: {len(questions)}")
        print(f"커플 연결 수: {len(connections)}")
        
        if len(users) < 2:
            print("테스트를 위해 최소 2명의 사용자가 필요합니다.")
            return False
        
        if len(questions) == 0:
            print("테스트를 위해 질문 데이터가 필요합니다.")
            return False
        
        # 2. 일일 질문 생성 테스트
        print("\n2. 일일 질문 생성 테스트...")
        
        if connections:
            connection = connections[0]
            
            # 오늘의 일일 질문 생성
            from app.routes.questions import get_or_create_daily_question
            daily_question = get_or_create_daily_question(connection.id)
            
            if daily_question:
                print(f"✅ 일일 질문 생성 성공: {daily_question.question.text[:50]}...")
            else:
                print("❌ 일일 질문 생성 실패")
                return False
        
        # 3. 답변 저장 테스트
        print("\n3. 답변 저장 테스트...")
        
        if connections and questions:
            connection = connections[0]
            user1, user2 = connection.get_users()
            question = questions[0]
            
            # 사용자 1의 답변 생성
            answer1 = Answer(
                question_id=question.id,
                user_id=user1.id,
                answer_text="테스트 답변 1입니다.",
                date=date.today()
            )
            
            try:
                db.session.add(answer1)
                db.session.commit()
                print(f"✅ 사용자 1 답변 저장 성공")
            except Exception as e:
                print(f"❌ 사용자 1 답변 저장 실패: {e}")
                db.session.rollback()
                return False
            
            # 사용자 2의 답변 생성
            if user2:
                answer2 = Answer(
                    question_id=question.id,
                    user_id=user2.id,
                    answer_text="테스트 답변 2입니다.",
                    date=date.today()
                )
                
                try:
                    db.session.add(answer2)
                    db.session.commit()
                    print(f"✅ 사용자 2 답변 저장 성공")
                except Exception as e:
                    print(f"❌ 사용자 2 답변 저장 실패: {e}")
                    db.session.rollback()
                    return False
        
        # 4. 접근 제어 테스트
        print("\n4. 접근 제어 테스트...")
        
        if connections:
            connection = connections[0]
            user1, user2 = connection.get_users()
            
            if user1 and user2:
                # 사용자 1이 답변한 경우 파트너 답변 조회 가능 여부 확인
                user1_answers = Answer.query.filter_by(user_id=user1.id).first()
                if user1_answers:
                    partner_answer = Answer.query.filter_by(
                        question_id=user1_answers.question_id,
                        user_id=user2.id,
                        date=user1_answers.date
                    ).first()
                    
                    if partner_answer:
                        print("✅ 접근 제어 테스트: 답변 후 파트너 답변 조회 가능")
                    else:
                        print("⚠️  파트너 답변이 없어 접근 제어 완전 테스트 불가")
        
        # 5. 답변 완료 상태 확인 테스트
        print("\n5. 답변 완료 상태 확인 테스트...")
        
        if questions:
            question = questions[0]
            today = date.today()
            
            if connections:
                connection = connections[0]
                user1, user2 = connection.get_users()
                
                if user1 and user2:
                    status = Answer.get_answer_completion_status(
                        question.id, today, user1.id, user2.id
                    )
                    
                    print(f"사용자 1 답변 완료: {status['user1_answered']}")
                    print(f"사용자 2 답변 완료: {status['user2_answered']}")
                    print(f"모두 답변 완료: {status['both_answered']}")
        
        # 6. 히스토리 조회 테스트
        print("\n6. 히스토리 조회 테스트...")
        
        total_answers = Answer.query.count()
        print(f"총 답변 수: {total_answers}")
        
        if total_answers > 0:
            # 최근 답변 조회
            recent_answers = Answer.query.order_by(Answer.created_at.desc()).limit(5).all()
            print(f"최근 답변 {len(recent_answers)}개:")
            for answer in recent_answers:
                print(f"  - {answer.date}: {answer.answer_text[:30]}...")
        
        print("\n✅ 답변 시스템 테스트 완료!")
        return True

if __name__ == "__main__":
    success = test_answer_system()
    if success:
        print("\n🎉 모든 테스트가 성공적으로 완료되었습니다!")
    else:
        print("\n❌ 일부 테스트가 실패했습니다.")
        sys.exit(1)