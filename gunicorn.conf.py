"""Gunicorn 설정 파일"""

import os
import multiprocessing

# 서버 소켓
bind = "0.0.0.0:5000"
backlog = 2048

# 워커 프로세스
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "eventlet"  # SocketIO 지원을 위해 eventlet 사용
worker_connections = 1000
timeout = 30
keepalive = 2

# 재시작 설정
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# 로깅
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 프로세스 이름
proc_name = "couple_app"

# 보안
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# 성능 튜닝
worker_tmp_dir = "/dev/shm"  # 메모리 기반 임시 디렉토리 (Linux)

def when_ready(server):
    """서버 준비 완료 시 실행"""
    server.log.info("서버가 준비되었습니다.")

def worker_int(worker):
    """워커 인터럽트 시 실행"""
    worker.log.info("워커가 인터럽트되었습니다.")

def pre_fork(server, worker):
    """워커 포크 전 실행"""
    server.log.info("워커를 포크합니다.")

def post_fork(server, worker):
    """워커 포크 후 실행"""
    server.log.info("워커 포크가 완료되었습니다.")

def post_worker_init(worker):
    """워커 초기화 후 실행"""
    worker.log.info("워커 초기화가 완료되었습니다.")

def worker_abort(worker):
    """워커 중단 시 실행"""
    worker.log.info("워커가 중단되었습니다.")