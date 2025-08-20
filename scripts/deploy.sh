#!/bin/bash

# 커플 웹 애플리케이션 배포 스크립트

set -e  # 오류 발생 시 스크립트 중단

echo "=== 커플 웹 애플리케이션 배포 시작 ==="

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 함수 정의
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 환경 변수 설정
export FLASK_ENV=production
export PYTHONPATH=$PWD

# 1. 의존성 확인
log_info "의존성 확인 중..."

if ! command -v python3 &> /dev/null; then
    log_error "Python3가 설치되지 않았습니다."
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    log_error "pip3가 설치되지 않았습니다."
    exit 1
fi

# 2. 가상환경 활성화
log_info "가상환경 활성화 중..."

if [ ! -d "venv" ]; then
    log_warn "가상환경이 없습니다. 새로 생성합니다."
    python3 -m venv venv
fi

source venv/bin/activate

# 3. 패키지 설치/업데이트
log_info "패키지 설치/업데이트 중..."

pip install --upgrade pip
pip install -r requirements.txt

# 프로덕션 전용 패키지 설치
pip install gunicorn eventlet psutil pillow

# 4. 필요한 디렉토리 생성
log_info "디렉토리 구조 생성 중..."

mkdir -p logs
mkdir -p backups
mkdir -p uploads
mkdir -p instance

# 5. 데이터베이스 초기화 (필요한 경우)
log_info "데이터베이스 확인 중..."

if [ ! -f "instance/couple_app.db" ]; then
    log_info "데이터베이스를 초기화합니다."
    python scripts/init_db.py
    python scripts/init_questions.py
else
    log_info "기존 데이터베이스를 사용합니다."
fi

# 6. 프로덕션 최적화 실행
log_info "프로덕션 최적화 실행 중..."

python scripts/optimize_production.py

# 7. 정적 파일 수집 및 압축
log_info "정적 파일 최적화 중..."

# CSS/JS 파일 압축 (선택사항)
if command -v uglifyjs &> /dev/null && command -v cleancss &> /dev/null; then
    log_info "CSS/JS 파일 압축 중..."
    
    # JavaScript 압축
    find static/js -name "*.js" ! -name "*.min.js" -exec sh -c '
        for file do
            uglifyjs "$file" -o "${file%.js}.min.js" -c -m
        done
    ' sh {} +
    
    # CSS 압축
    find static/css -name "*.css" ! -name "*.min.css" -exec sh -c '
        for file do
            cleancss -o "${file%.css}.min.css" "$file"
        done
    ' sh {} +
else
    log_warn "uglifyjs 또는 cleancss가 설치되지 않아 파일 압축을 건너뜁니다."
fi

# 8. 설정 파일 확인
log_info "설정 파일 확인 중..."

if [ ! -f ".env" ]; then
    log_warn ".env 파일이 없습니다. 환경 변수를 확인하세요."
    
    # 기본 .env 파일 생성
    cat > .env << EOF
FLASK_ENV=production
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
DATABASE_URL=sqlite:///instance/couple_app.db
EOF
    
    log_info "기본 .env 파일을 생성했습니다. 필요에 따라 수정하세요."
fi

# 9. 권한 설정
log_info "파일 권한 설정 중..."

chmod +x scripts/*.py
chmod +x scripts/*.sh
chmod 755 uploads
chmod 755 logs
chmod 755 instance

# 10. 서비스 상태 확인
log_info "애플리케이션 테스트 중..."

# 간단한 애플리케이션 테스트
timeout 10s python -c "
from app.create_app import create_app
app = create_app('production')
with app.app_context():
    print('애플리케이션이 정상적으로 로드되었습니다.')
" || {
    log_error "애플리케이션 테스트 실패"
    exit 1
}

# 11. 백업 생성 (기존 데이터가 있는 경우)
if [ -f "instance/couple_app.db" ]; then
    log_info "데이터베이스 백업 생성 중..."
    
    backup_file="backups/couple_app_$(date +%Y%m%d_%H%M%S).db"
    cp "instance/couple_app.db" "$backup_file"
    
    log_info "백업 파일 생성: $backup_file"
fi

# 12. 배포 완료 메시지
log_info "=== 배포 완료 ==="

echo ""
echo "다음 명령어로 애플리케이션을 시작할 수 있습니다:"
echo ""
echo "개발 환경:"
echo "  source venv/bin/activate && python run.py"
echo ""
echo "프로덕션 환경 (Gunicorn):"
echo "  source venv/bin/activate && gunicorn -c gunicorn.conf.py wsgi:application"
echo ""
echo "시스템 서비스로 등록하려면 systemd 서비스 파일을 생성하세요."
echo ""

# 13. 추가 설정 안내
log_warn "추가 설정이 필요할 수 있습니다:"
echo "  - Nginx 설정 (nginx.conf.example 참조)"
echo "  - SSL 인증서 설정"
echo "  - 방화벽 설정"
echo "  - 로그 로테이션 설정"
echo "  - 모니터링 설정"

deactivate