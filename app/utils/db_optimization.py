"""데이터베이스 최적화 유틸리티"""

from app.extensions import db

def create_database_indexes():
    """성능 최적화를 위한 데이터베이스 인덱스 생성"""
    
    # 기존 인덱스 외에 추가로 필요한 인덱스들
    indexes = [
        # 커플 연결 관련 인덱스
        "CREATE INDEX IF NOT EXISTS idx_couple_connections_users ON couple_connections(user1_id, user2_id);",
        
        # D-Day 관련 인덱스
        "CREATE INDEX IF NOT EXISTS idx_ddays_couple_date ON ddays(couple_id, target_date);",
        "CREATE INDEX IF NOT EXISTS idx_ddays_created_by ON ddays(created_by);",
        
        # 이벤트 관련 인덱스
        "CREATE INDEX IF NOT EXISTS idx_events_couple_datetime ON events(couple_id, start_datetime);",
        "CREATE INDEX IF NOT EXISTS idx_events_participant ON events(participant_type);",
        "CREATE INDEX IF NOT EXISTS idx_events_created_by ON events(created_by);",
        
        # 질문 관련 인덱스
        "CREATE INDEX IF NOT EXISTS idx_questions_category ON questions(category);",
        "CREATE INDEX IF NOT EXISTS idx_questions_difficulty ON questions(difficulty);",
        "CREATE INDEX IF NOT EXISTS idx_daily_questions_date ON daily_questions(date);",
        
        # 답변 관련 인덱스
        "CREATE INDEX IF NOT EXISTS idx_answers_user_date ON answers(user_id, date);",
        "CREATE INDEX IF NOT EXISTS idx_answers_question_date ON answers(question_id, date);",
        
        # 메모리 관련 인덱스
        "CREATE INDEX IF NOT EXISTS idx_memories_couple_date ON memories(couple_id, memory_date);",
        "CREATE INDEX IF NOT EXISTS idx_memories_created_by ON memories(created_by);",
        
        # 무드 엔트리 관련 인덱스
        "CREATE INDEX IF NOT EXISTS idx_mood_entries_user_date ON mood_entries(user_id, date);",
        "CREATE INDEX IF NOT EXISTS idx_mood_entries_date ON mood_entries(date);",
        
        # 알림 관련 인덱스
        "CREATE INDEX IF NOT EXISTS idx_notifications_user_read ON notifications(user_id, is_read);",
        "CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(type);",
        "CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);",
    ]
    
    try:
        for index_sql in indexes:
            db.session.execute(db.text(index_sql))
        
        db.session.commit()
        print("데이터베이스 인덱스가 성공적으로 생성되었습니다.")
        return True
        
    except Exception as e:
        print(f"인덱스 생성 중 오류 발생: {e}")
        return False

def analyze_query_performance():
    """쿼리 성능 분석을 위한 EXPLAIN 실행"""
    
    # 주요 쿼리들의 실행 계획 분석
    queries_to_analyze = [
        # 사용자의 커플 연결 조회
        """
        EXPLAIN QUERY PLAN 
        SELECT * FROM couple_connections 
        WHERE user1_id = 1 OR user2_id = 1;
        """,
        
        # 커플의 D-Day 목록 조회
        """
        EXPLAIN QUERY PLAN 
        SELECT * FROM ddays 
        WHERE couple_id = 1 
        ORDER BY target_date ASC;
        """,
        
        # 월별 이벤트 조회
        """
        EXPLAIN QUERY PLAN 
        SELECT * FROM events 
        WHERE couple_id = 1 
        AND start_datetime >= '2024-01-01' 
        AND start_datetime < '2024-02-01'
        ORDER BY start_datetime ASC;
        """,
        
        # 사용자의 최근 답변 조회
        """
        EXPLAIN QUERY PLAN 
        SELECT a.*, q.text FROM answers a
        JOIN questions q ON a.question_id = q.id
        WHERE a.user_id = 1
        ORDER BY a.date DESC
        LIMIT 10;
        """,
        
        # 사용자의 월별 기분 통계
        """
        EXPLAIN QUERY PLAN 
        SELECT mood_level, COUNT(*) FROM mood_entries
        WHERE user_id = 1 
        AND date >= '2024-01-01' 
        AND date < '2024-02-01'
        GROUP BY mood_level;
        """,
        
        # 읽지 않은 알림 조회
        """
        EXPLAIN QUERY PLAN 
        SELECT * FROM notifications
        WHERE user_id = 1 AND is_read = 0
        ORDER BY created_at DESC;
        """
    ]
    
    print("=== 쿼리 성능 분석 결과 ===")
    
    try:
        for i, query in enumerate(queries_to_analyze, 1):
            print(f"\n{i}. 쿼리 분석:")
            print(query.strip())
            print("-" * 50)
            
            result = db.session.execute(db.text(query))
            for row in result:
                print(row)
                
    except Exception as e:
        print(f"쿼리 분석 중 오류 발생: {e}")

def optimize_database_settings():
    """SQLite 데이터베이스 최적화 설정"""
    
    optimization_queries = [
        # WAL 모드 활성화 (동시성 향상)
        "PRAGMA journal_mode = WAL;",
        
        # 동기화 모드 최적화 (성능 향상)
        "PRAGMA synchronous = NORMAL;",
        
        # 캐시 크기 증가 (메모리 사용량 증가하지만 성능 향상)
        "PRAGMA cache_size = -64000;",  # 64MB 캐시
        
        # 임시 저장소를 메모리에 설정
        "PRAGMA temp_store = MEMORY;",
        
        # 자동 VACUUM 활성화
        "PRAGMA auto_vacuum = INCREMENTAL;",
        
        # 외래 키 제약 조건 활성화
        "PRAGMA foreign_keys = ON;",
    ]
    
    try:
        for pragma_sql in optimization_queries:
            db.session.execute(db.text(pragma_sql))
        
        db.session.commit()
        print("데이터베이스 최적화 설정이 완료되었습니다.")
        return True
        
    except Exception as e:
        print(f"데이터베이스 최적화 설정 중 오류 발생: {e}")
        return False

def vacuum_database():
    """데이터베이스 VACUUM 실행 (공간 최적화)"""
    
    try:
        # 증분 VACUUM 실행
        db.session.execute(db.text("PRAGMA incremental_vacuum;"))
        
        # 통계 정보 업데이트
        db.session.execute(db.text("ANALYZE;"))
        
        db.session.commit()
        
        print("데이터베이스 VACUUM 및 통계 업데이트가 완료되었습니다.")
        return True
        
    except Exception as e:
        print(f"데이터베이스 VACUUM 중 오류 발생: {e}")
        return False