#!/usr/bin/env python3
"""프로덕션 환경 최적화 스크립트"""

import os
import sys
import logging
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.create_app import create_app
from app.utils.db_optimization import create_database_indexes, optimize_database_settings, vacuum_database
from app.extensions import db
from app.utils.static_optimization import StaticFileOptimizer, optimize_images, create_webp_versions
from app.services.query_optimization import OptimizedQueryService

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

def optimize_database(app):
    """데이터베이스 최적화 실행"""
    logger = logging.getLogger(__name__)
    
    logger.info("데이터베이스 최적화 시작...")
    
    # 인덱스 생성
    logger.info("인덱스 생성 중...")
    if create_database_indexes():
        logger.info("인덱스 생성 완료")
    else:
        logger.error("인덱스 생성 실패")
    
    # 데이터베이스 설정 최적화
    logger.info("데이터베이스 설정 최적화 중...")
    if optimize_database_settings():
        logger.info("데이터베이스 설정 최적화 완료")
    else:
        logger.error("데이터베이스 설정 최적화 실패")
    
    # VACUUM 실행
    logger.info("데이터베이스 VACUUM 실행 중...")
    if vacuum_database():
        logger.info("데이터베이스 VACUUM 완료")
    else:
        logger.error("데이터베이스 VACUUM 실패")
    
    # 데이터베이스 통계 출력
    try:
        stats = OptimizedQueryService.get_database_statistics()
        logger.info(f"데이터베이스 통계: {stats}")
    except Exception as e:
        logger.error(f"데이터베이스 통계 조회 실패: {e}")

def optimize_static_files(app):
    """정적 파일 최적화 실행"""
    logger = logging.getLogger(__name__)
    
    logger.info("정적 파일 최적화 시작...")
    
    # 정적 파일 압축 (애플리케이션 컨텍스트 필요)
    logger.info("정적 파일 압축 중...")
    try:
        with app.app_context():
            compressed_count = StaticFileOptimizer.compress_static_files()
            logger.info(f"{compressed_count}개 파일 압축 완료")
    except Exception as e:
        logger.error(f"정적 파일 압축 실패: {e}")
    
    # 이미지 최적화 (애플리케이션 컨텍스트 필요)
    logger.info("이미지 최적화 중...")
    try:
        with app.app_context():
            optimized_count = optimize_images()
            logger.info(f"{optimized_count}개 이미지 최적화 완료")
    except ImportError:
        logger.warning("PIL/Pillow가 설치되지 않아 이미지 최적화를 건너뜁니다.")
    except Exception as e:
        logger.error(f"이미지 최적화 실패: {e}")
    
    # WebP 버전 생성 (애플리케이션 컨텍스트 필요)
    logger.info("WebP 이미지 생성 중...")
    try:
        with app.app_context():
            webp_count = create_webp_versions()
            logger.info(f"{webp_count}개 WebP 이미지 생성 완료")
    except ImportError:
        logger.warning("PIL/Pillow가 설치되지 않아 WebP 생성을 건너뜁니다.")
    except Exception as e:
        logger.error(f"WebP 생성 실패: {e}")

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
                os.remove(file_path)
                logger.info(f"오래된 로그 파일 삭제: {filename}")

def run_optimization():
    """전체 최적화 프로세스 실행"""
    logger = setup_logging()
    
    logger.info("=== 프로덕션 환경 최적화 시작 ===")
    start_time = datetime.now()
    
    try:
        # Flask 애플리케이션 생성
        app = create_app('production')
        
        # 필요한 디렉토리 생성
        create_production_directories()
        
        # 데이터베이스 최적화
        with app.app_context():
            optimize_database(app)
        
        # 정적 파일 최적화
        optimize_static_files(app)
        
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