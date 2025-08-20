#!/usr/bin/env python3
"""유지보수 및 정리 스크립트"""

import os
import sys
import argparse
import logging
from datetime import datetime, timedelta

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.create_app import create_app
from app.extensions import db
from app.services.query_optimization import OptimizedQueryService
from app.utils.db_optimization import vacuum_database, analyze_query_performance
from app.models.notification import Notification

def setup_logging():
    """로깅 설정"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('maintenance.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def cleanup_old_notifications(app, days=30):
    """오래된 알림 정리"""
    logger = logging.getLogger(__name__)
    
    with app.app_context():
        deleted_count = OptimizedQueryService.cleanup_old_notifications(days)
        logger.info(f"{deleted_count}개의 오래된 알림을 정리했습니다.")
        return deleted_count

def cleanup_old_logs(days=30):
    """오래된 로그 파일 정리"""
    logger = logging.getLogger(__name__)
    
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        return 0
    
    cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
    deleted_count = 0
    
    for filename in os.listdir(log_dir):
        file_path = os.path.join(log_dir, filename)
        
        if os.path.isfile(file_path) and os.path.getmtime(file_path) < cutoff_time:
            try:
                os.remove(file_path)
                logger.info(f"오래된 로그 파일 삭제: {filename}")
                deleted_count += 1
            except OSError as e:
                logger.error(f"로그 파일 삭제 실패 {filename}: {e}")
    
    logger.info(f"{deleted_count}개의 오래된 로그 파일을 정리했습니다.")
    return deleted_count

def backup_database(app):
    """데이터베이스 백업"""
    logger = logging.getLogger(__name__)
    
    with app.app_context():
        # SQLite 데이터베이스 파일 경로
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        if not os.path.exists(db_path):
            logger.error(f"데이터베이스 파일을 찾을 수 없습니다: {db_path}")
            return False
        
        # 백업 디렉토리 생성
        backup_dir = 'backups'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # 백업 파일명 생성
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"couple_app_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        try:
            # 파일 복사
            import shutil
            shutil.copy2(db_path, backup_path)
            
            logger.info(f"데이터베이스 백업 완료: {backup_path}")
            
            # 백업 파일 크기 확인
            backup_size = os.path.getsize(backup_path)
            logger.info(f"백업 파일 크기: {backup_size / 1024 / 1024:.2f} MB")
            
            return backup_path
            
        except Exception as e:
            logger.error(f"데이터베이스 백업 실패: {e}")
            return False

def cleanup_old_backups(days=90):
    """오래된 백업 파일 정리"""
    logger = logging.getLogger(__name__)
    
    backup_dir = 'backups'
    if not os.path.exists(backup_dir):
        return 0
    
    cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
    deleted_count = 0
    
    for filename in os.listdir(backup_dir):
        if filename.startswith('couple_app_backup_') and filename.endswith('.db'):
            file_path = os.path.join(backup_dir, filename)
            
            if os.path.isfile(file_path) and os.path.getmtime(file_path) < cutoff_time:
                try:
                    os.remove(file_path)
                    logger.info(f"오래된 백업 파일 삭제: {filename}")
                    deleted_count += 1
                except OSError as e:
                    logger.error(f"백업 파일 삭제 실패 {filename}: {e}")
    
    logger.info(f"{deleted_count}개의 오래된 백업 파일을 정리했습니다.")
    return deleted_count

def optimize_database(app):
    """데이터베이스 최적화"""
    logger = logging.getLogger(__name__)
    
    with app.app_context():
        logger.info("데이터베이스 최적화 시작...")
        
        # VACUUM 실행
        if vacuum_database():
            logger.info("데이터베이스 VACUUM 완료")
        else:
            logger.error("데이터베이스 VACUUM 실패")
        
        # 통계 정보 출력
        stats = OptimizedQueryService.get_database_statistics()
        logger.info(f"데이터베이스 통계: {stats}")

def generate_maintenance_report(app):
    """유지보수 보고서 생성"""
    logger = logging.getLogger(__name__)
    
    with app.app_context():
        # 데이터베이스 통계
        db_stats = OptimizedQueryService.get_database_statistics()
        
        # 디스크 사용량
        def get_directory_size(path):
            total_size = 0
            if os.path.exists(path):
                for dirpath, dirnames, filenames in os.walk(path):
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        if os.path.exists(filepath):
                            total_size += os.path.getsize(filepath)
            return total_size
        
        upload_size = get_directory_size('uploads')
        log_size = get_directory_size('logs')
        backup_size = get_directory_size('backups')
        
        # 보고서 생성
        report = {
            'timestamp': datetime.now().isoformat(),
            'database_stats': db_stats,
            'disk_usage': {
                'uploads_mb': upload_size / 1024 / 1024,
                'logs_mb': log_size / 1024 / 1024,
                'backups_mb': backup_size / 1024 / 1024
            }
        }
        
        # 보고서 파일 저장
        report_filename = f"maintenance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = os.path.join('logs', report_filename)
        
        import json
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"유지보수 보고서 생성: {report_path}")
        return report_path

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='커플 웹 애플리케이션 유지보수 스크립트')
    parser.add_argument('--cleanup-notifications', type=int, default=30, 
                       help='지정된 일수보다 오래된 읽은 알림 정리 (기본: 30일)')
    parser.add_argument('--cleanup-logs', type=int, default=30,
                       help='지정된 일수보다 오래된 로그 파일 정리 (기본: 30일)')
    parser.add_argument('--cleanup-backups', type=int, default=90,
                       help='지정된 일수보다 오래된 백업 파일 정리 (기본: 90일)')
    parser.add_argument('--backup', action='store_true',
                       help='데이터베이스 백업 생성')
    parser.add_argument('--optimize', action='store_true',
                       help='데이터베이스 최적화 실행')
    parser.add_argument('--report', action='store_true',
                       help='유지보수 보고서 생성')
    parser.add_argument('--all', action='store_true',
                       help='모든 유지보수 작업 실행')
    
    args = parser.parse_args()
    
    # 로깅 설정
    logger = setup_logging()
    
    # Flask 애플리케이션 생성
    app = create_app('production')
    
    logger.info("=== 유지보수 작업 시작 ===")
    
    try:
        if args.all or args.backup:
            backup_database(app)
        
        if args.all or args.cleanup_notifications:
            cleanup_old_notifications(app, args.cleanup_notifications)
        
        if args.all or args.cleanup_logs:
            cleanup_old_logs(args.cleanup_logs)
        
        if args.all or args.cleanup_backups:
            cleanup_old_backups(args.cleanup_backups)
        
        if args.all or args.optimize:
            optimize_database(app)
        
        if args.all or args.report:
            generate_maintenance_report(app)
        
        logger.info("=== 유지보수 작업 완료 ===")
        
    except Exception as e:
        logger.error(f"유지보수 작업 중 오류 발생: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()