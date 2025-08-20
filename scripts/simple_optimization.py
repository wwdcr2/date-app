#!/usr/bin/env python3
"""간단한 프로덕션 환경 최적화 스크립트"""

import os
import sys
import logging
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def setup_logging():
    """로깅 설정"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('optimization.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def create_production_directories():
    """프로덕션 환경에 필요한 디렉토리 생성"""
    logger = logging.getLogger(__name__)
    
    directories = [
        'logs',
        'backups',
        'uploads',
        'instance'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"디렉토리 생성: {directory}")

def optimize_database():
    """데이터베이스 최적화 실행"""
    logger = logging.getLogger(__name__)
    
    from app.create_app import create_app
    
    app = create_app('production')
    
    with app.app_context():
        from app.extensions import db
        
        logger.info("데이터베이스 최적화 시작...")
        
        # 기본 인덱스들 생성
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_couple_connections_users ON couple_connections(user1_id, user2_id);",
            "CREATE INDEX IF NOT EXISTS idx_ddays_couple_date ON ddays(couple_id, target_date);",
            "CREATE INDEX IF NOT EXISTS idx_events_couple_datetime ON events(couple_id, start_datetime);",
            "CREATE INDEX IF NOT EXISTS idx_answers_user_date ON answers(user_id, date);",
            "CREATE INDEX IF NOT EXISTS idx_memories_couple_date ON memories(couple_id, memory_date);",
            "CREATE INDEX IF NOT EXISTS idx_mood_entries_user_date ON mood_entries(user_id, date);",
            "CREATE INDEX IF NOT EXISTS idx_notifications_user_read ON notifications(user_id, is_read);",
        ]
        
        try:
            for index_sql in indexes:
                db.session.execute(db.text(index_sql))
            
            db.session.commit()
            logger.info("데이터베이스 인덱스 생성 완료")
            
        except Exception as e:
            logger.error(f"인덱스 생성 실패: {e}")
            db.session.rollback()
        
        # 데이터베이스 최적화 설정
        try:
            optimization_queries = [
                "PRAGMA journal_mode = WAL;",
                "PRAGMA synchronous = NORMAL;",
                "PRAGMA cache_size = -64000;",
                "PRAGMA temp_store = MEMORY;",
                "PRAGMA foreign_keys = ON;",
            ]
            
            for pragma_sql in optimization_queries:
                db.session.execute(db.text(pragma_sql))
            
            db.session.commit()
            logger.info("데이터베이스 최적화 설정 완료")
            
        except Exception as e:
            logger.error(f"데이터베이스 최적화 설정 실패: {e}")
        
        # VACUUM 실행
        try:
            db.session.execute(db.text("PRAGMA incremental_vacuum;"))
            db.session.execute(db.text("ANALYZE;"))
            db.session.commit()
            logger.info("데이터베이스 VACUUM 완료")
            
        except Exception as e:
            logger.error(f"데이터베이스 VACUUM 실패: {e}")

def compress_static_files():
    """정적 파일 압축"""
    logger = logging.getLogger(__name__)
    
    import gzip
    import shutil
    
    static_folder = 'static'
    if not os.path.exists(static_folder):
        logger.warning("static 폴더가 존재하지 않습니다.")
        return 0
    
    compressible_extensions = ['.css', '.js', '.html', '.svg', '.json']
    compressed_count = 0
    
    for root, dirs, files in os.walk(static_folder):
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1].lower()
            
            if file_ext in compressible_extensions:
                gzip_path = file_path + '.gz'
                
                # 원본 파일이 더 최신이거나 gzip 파일이 없는 경우에만 압축
                if (not os.path.exists(gzip_path) or 
                    os.path.getmtime(file_path) > os.path.getmtime(gzip_path)):
                    
                    try:
                        with open(file_path, 'rb') as f_in:
                            with gzip.open(gzip_path, 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                        
                        compressed_count += 1
                        logger.info(f"압축 완료: {file_path}")
                        
                    except Exception as e:
                        logger.error(f"압축 실패 {file_path}: {e}")
    
    logger.info(f"총 {compressed_count}개 파일이 압축되었습니다.")
    return compressed_count

def cleanup_old_files():
    """오래된 파일 정리"""
    logger = logging.getLogger(__name__)
    
    # 오래된 로그 파일 정리 (30일 이상)
    log_dir = 'logs'
    if os.path.exists(log_dir):
        cutoff_time = datetime.now().timestamp() - (30 * 24 * 3600)  # 30일
        
        for filename in os.listdir(log_dir):
            file_path = os.path.join(log_dir, filename)
            if os.path.isfile(file_path) and os.path.getmtime(file_path) < cutoff_time:
                try:
                    os.remove(file_path)
                    logger.info(f"오래된 로그 파일 삭제: {filename}")
                except OSError as e:
                    logger.error(f"로그 파일 삭제 실패 {filename}: {e}")

def run_optimization():
    """전체 최적화 프로세스 실행"""
    logger = setup_logging()
    
    logger.info("=== 간단한 프로덕션 환경 최적화 시작 ===")
    start_time = datetime.now()
    
    try:
        # 필요한 디렉토리 생성
        create_production_directories()
        
        # 데이터베이스 최적화
        optimize_database()
        
        # 정적 파일 압축
        compress_static_files()
        
        # 오래된 파일 정리
        cleanup_old_files()
        
        # 완료 시간 계산
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info(f"=== 최적화 완료 (소요시간: {duration}) ===")
        
    except Exception as e:
        logger.error(f"최적화 중 오류 발생: {e}")
        sys.exit(1)

if __name__ == '__main__':
    run_optimization()