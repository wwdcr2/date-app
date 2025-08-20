"""성능 모니터링 유틸리티"""

import time
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
import logging
from datetime import datetime
from functools import wraps
from flask import request, g, current_app
from app.extensions import db

# 성능 로거 설정
performance_logger = logging.getLogger('performance')
performance_logger.setLevel(logging.INFO)

class PerformanceMonitor:
    """성능 모니터링 클래스"""
    
    @staticmethod
    def get_system_stats():
        """시스템 리소스 사용량 조회"""
        if not PSUTIL_AVAILABLE:
            return {
                'cpu_percent': 'N/A (psutil not installed)',
                'memory_percent': 'N/A (psutil not installed)',
                'disk_usage': 'N/A (psutil not installed)',
                'timestamp': datetime.utcnow().isoformat()
            }
        
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def get_database_stats():
        """데이터베이스 성능 통계"""
        try:
            # SQLite 통계 조회
            stats = {}
            
            # 데이터베이스 크기
            db_size_result = db.session.execute(db.text("PRAGMA page_count;")).fetchone()
            page_size_result = db.session.execute(db.text("PRAGMA page_size;")).fetchone()
            
            if db_size_result and page_size_result:
                stats['db_size_mb'] = (db_size_result[0] * page_size_result[0]) / (1024 * 1024)
            
            # 캐시 히트율
            cache_stats = db.session.execute(db.text("PRAGMA cache_size;")).fetchone()
            if cache_stats:
                stats['cache_size'] = cache_stats[0]
            
            # WAL 모드 확인
            wal_mode = db.session.execute(db.text("PRAGMA journal_mode;")).fetchone()
            if wal_mode:
                stats['journal_mode'] = wal_mode[0]
            
            return stats
            
        except Exception as e:
            performance_logger.error(f"데이터베이스 통계 조회 실패: {e}")
            return {}
    
    @staticmethod
    def log_slow_query(query, duration, threshold=1.0):
        """느린 쿼리 로깅"""
        if duration > threshold:
            performance_logger.warning(
                f"Slow query detected: {duration:.2f}s - {query[:200]}..."
            )

def monitor_request_performance(f):
    """요청 성능 모니터링 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = f(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            
            # 느린 요청 로깅 (1초 이상)
            if duration > 1.0:
                performance_logger.warning(
                    f"Slow request: {request.method} {request.path} - {duration:.2f}s"
                )
            
            # 성능 메트릭 저장 (선택적)
            if hasattr(g, 'performance_metrics'):
                g.performance_metrics['request_duration'] = duration
    
    return decorated_function

def monitor_database_queries():
    """데이터베이스 쿼리 모니터링 설정"""
    import sqlalchemy
    from sqlalchemy import event
    
    @event.listens_for(db.engine, "before_cursor_execute")
    def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        context._query_start_time = time.time()
    
    @event.listens_for(db.engine, "after_cursor_execute")
    def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        total = time.time() - context._query_start_time
        
        # 느린 쿼리 로깅
        PerformanceMonitor.log_slow_query(statement, total)
        
        # 성능 메트릭에 추가
        if hasattr(g, 'performance_metrics'):
            if 'db_queries' not in g.performance_metrics:
                g.performance_metrics['db_queries'] = []
            
            g.performance_metrics['db_queries'].append({
                'query': statement[:100] + '...' if len(statement) > 100 else statement,
                'duration': total,
                'timestamp': datetime.utcnow().isoformat()
            })

class RequestProfiler:
    """요청 프로파일링 클래스"""
    
    def __init__(self):
        self.profiles = []
    
    def start_profiling(self):
        """프로파일링 시작"""
        g.profile_start = time.time()
        g.performance_metrics = {
            'start_time': datetime.utcnow().isoformat(),
            'endpoint': request.endpoint,
            'method': request.method,
            'path': request.path
        }
    
    def end_profiling(self, response):
        """프로파일링 종료"""
        if hasattr(g, 'profile_start'):
            duration = time.time() - g.profile_start
            
            if hasattr(g, 'performance_metrics'):
                g.performance_metrics.update({
                    'total_duration': duration,
                    'status_code': response.status_code,
                    'response_size': len(response.get_data()),
                    'end_time': datetime.utcnow().isoformat()
                })
                
                # 성능 데이터 저장 (개발 환경에서만)
                if current_app.debug:
                    self.profiles.append(g.performance_metrics.copy())
                    
                    # 최근 100개 요청만 유지
                    if len(self.profiles) > 100:
                        self.profiles = self.profiles[-100:]
        
        return response
    
    def get_recent_profiles(self, limit=20):
        """최근 프로파일 데이터 반환"""
        return self.profiles[-limit:] if self.profiles else []
    
    def get_slow_requests(self, threshold=1.0, limit=10):
        """느린 요청 목록 반환"""
        slow_requests = [
            profile for profile in self.profiles 
            if profile.get('total_duration', 0) > threshold
        ]
        return sorted(slow_requests, key=lambda x: x.get('total_duration', 0), reverse=True)[:limit]

# 전역 프로파일러 인스턴스
request_profiler = RequestProfiler()

def init_performance_monitoring(app):
    """성능 모니터링 초기화"""
    
    # 로깅 설정
    if not app.debug:
        handler = logging.FileHandler('logs/performance.log')
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s'
        )
        handler.setFormatter(formatter)
        performance_logger.addHandler(handler)
    
    # 데이터베이스 쿼리 모니터링 활성화
    monitor_database_queries()
    
    # 요청 전/후 처리
    @app.before_request
    def before_request():
        request_profiler.start_profiling()
    
    @app.after_request
    def after_request(response):
        return request_profiler.end_profiling(response)
    
    # 성능 통계 엔드포인트 (개발 환경에서만)
    if app.debug:
        @app.route('/debug/performance')
        def performance_stats():
            from flask import jsonify
            
            return jsonify({
                'system_stats': PerformanceMonitor.get_system_stats(),
                'database_stats': PerformanceMonitor.get_database_stats(),
                'recent_requests': request_profiler.get_recent_profiles(),
                'slow_requests': request_profiler.get_slow_requests()
            })

def create_performance_report():
    """성능 보고서 생성"""
    report = {
        'timestamp': datetime.utcnow().isoformat(),
        'system_stats': PerformanceMonitor.get_system_stats(),
        'database_stats': PerformanceMonitor.get_database_stats(),
        'recent_profiles': request_profiler.get_recent_profiles(50),
        'slow_requests': request_profiler.get_slow_requests(threshold=0.5, limit=20)
    }
    
    return report