#!/usr/bin/env python3
"""
답변 모델 마이그레이션 스크립트
기존 daily_question_id 기반에서 question_id + date 기반으로 변경
"""

import sys
import os
from datetime import datetime, date

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.create_app import create_app
from app.extensions import db
from app.models.question import Question, Answer, DailyQuestion
from app.models.couple import CoupleConnection

def migrate_answer_model():
    """답변 모델을 새로운 구조로 마이그레이션"""
    app = create_app()
    
    with app.app_context():
        print("답변 모델 마이그레이션 시작...")
        
        # 1. 기존 데이터 백업
        print("1. 기존 데이터 조회 중...")
        
        # 기존 answers 테이블의 모든 데이터 조회
        existing_answers = db.session.execute(
            db.text("SELECT id, daily_question_id, user_id, answer_text, answered_at FROM answers")
        ).fetchall()
        
        print(f"기존 답변 데이터: {len(existing_answers)}개")
        
        # 2. 새로운 테이블 구조 생성을 위해 기존 테이블 삭제
        print("2. 기존 테이블 구조 변경 중...")
        
        # 기존 answers 테이블 삭제
        db.session.execute(db.text("DROP TABLE IF EXISTS answers"))
        
        # 새로운 구조로 테이블 재생성
        db.create_all()
        
        # 3. 데이터 마이그레이션
        print("3. 데이터 마이그레이션 중...")
        
        migrated_count = 0
        error_count = 0
        
        for old_answer in existing_answers:
            try:
                # daily_question 정보 조회
                daily_question = DailyQuestion.query.get(old_answer.daily_question_id)
                
                if not daily_question:
                    print(f"Warning: daily_question_id {old_answer.daily_question_id}를 찾을 수 없습니다.")
                    error_count += 1
                    continue
                
                # 새로운 Answer 객체 생성
                new_answer = Answer(
                    question_id=daily_question.question_id,
                    user_id=old_answer.user_id,
                    answer_text=old_answer.answer_text,
                    date=daily_question.date,
                    created_at=old_answer.answered_at,
                    updated_at=old_answer.answered_at
                )
                
                db.session.add(new_answer)
                migrated_count += 1
                
            except Exception as e:
                print(f"Error migrating answer {old_answer.id}: {e}")
                error_count += 1
                continue
        
        # 4. 변경사항 커밋
        try:
            db.session.commit()
            print(f"4. 마이그레이션 완료: {migrated_count}개 성공, {error_count}개 실패")
        except Exception as e:
            db.session.rollback()
            print(f"Error committing changes: {e}")
            return False
        
        # 5. 마이그레이션 결과 확인
        print("5. 마이그레이션 결과 확인...")
        
        new_answer_count = Answer.query.count()
        print(f"새로운 답변 테이블 레코드 수: {new_answer_count}")
        
        # 테이블 구조 확인
        inspector = db.inspect(db.engine)
        columns = inspector.get_columns('answers')
        print("새로운 answers 테이블 구조:")
        for col in columns:
            print(f"  {col['name']}: {col['type']}")
        
        return True

def verify_migration():
    """마이그레이션 결과 검증"""
    app = create_app()
    
    with app.app_context():
        print("\n마이그레이션 검증 중...")
        
        # 1. 기본 통계
        total_answers = Answer.query.count()
        total_questions = Question.query.count()
        total_daily_questions = DailyQuestion.query.count()
        
        print(f"총 답변 수: {total_answers}")
        print(f"총 질문 수: {total_questions}")
        print(f"총 일일 질문 수: {total_daily_questions}")
        
        # 2. 날짜별 답변 통계
        from sqlalchemy import func
        date_stats = db.session.query(
            Answer.date,
            func.count(Answer.id).label('count')
        ).group_by(Answer.date).order_by(Answer.date.desc()).limit(10).all()
        
        print("\n최근 날짜별 답변 통계:")
        for date_stat in date_stats:
            print(f"  {date_stat.date}: {date_stat.count}개")
        
        # 3. 중복 검사
        duplicates = db.session.query(
            Answer.question_id,
            Answer.user_id,
            Answer.date,
            func.count(Answer.id).label('count')
        ).group_by(
            Answer.question_id,
            Answer.user_id,
            Answer.date
        ).having(func.count(Answer.id) > 1).all()
        
        if duplicates:
            print(f"\n경고: {len(duplicates)}개의 중복 답변이 발견되었습니다:")
            for dup in duplicates:
                print(f"  질문 {dup.question_id}, 사용자 {dup.user_id}, 날짜 {dup.date}: {dup.count}개")
        else:
            print("\n✅ 중복 답변 없음")
        
        return len(duplicates) == 0

if __name__ == "__main__":
    print("답변 모델 마이그레이션을 시작합니다...")
    print("이 작업은 기존 데이터를 변경합니다. 계속하시겠습니까? (y/N): ", end="")
    
    response = input().strip().lower()
    if response != 'y':
        print("마이그레이션이 취소되었습니다.")
        sys.exit(0)
    
    success = migrate_answer_model()
    
    if success:
        verify_migration()
        print("\n✅ 마이그레이션이 성공적으로 완료되었습니다!")
    else:
        print("\n❌ 마이그레이션 중 오류가 발생했습니다.")
        sys.exit(1)