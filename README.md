# 커플 웹 애플리케이션

커플을 위한 미니멀한 웹 애플리케이션입니다. D-Day, 캘린더, 랜덤 질문, 메모리 북, 무드 트래커 등의 기능을 제공합니다.

## 기능

- 🗓️ **D-Day 관리**: 특별한 날까지의 남은 시간 확인
- 📅 **캘린더 & 일정**: 함께하는 일정 관리 (참여자별 구분)
- ❓ **랜덤 질문**: 매일 서로 다른 질문으로 더 깊이 알아가기
- 📖 **메모리 북**: 함께한 추억 기록 및 사진 저장
- 😊 **무드 트래커**: 일일 기분 공유 및 히스토리 관리
- 🔔 **실시간 알림**: WebSocket 기반 실시간 업데이트

## 기술 스택

- **Backend**: Flask, Flask-SocketIO, SQLAlchemy
- **Database**: SQLite (로컬 개발)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Real-time**: WebSocket (Socket.IO)

## 설치 및 실행

### 1. 가상환경 생성 및 활성화
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate     # Windows
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정
`.env` 파일을 확인하고 필요시 수정하세요.

### 4. 애플리케이션 실행
```bash
python run.py
```

애플리케이션이 `http://127.0.0.1:5000`에서 실행됩니다.

## 프로젝트 구조

```
couple-web-app/
├── app/
│   ├── models/          # 데이터베이스 모델
│   ├── routes/          # 라우트 핸들러
│   ├── services/        # 비즈니스 로직
│   ├── utils/           # 유틸리티 함수
│   ├── create_app.py    # 애플리케이션 팩토리
│   └── extensions.py    # Flask 확장 모듈
├── templates/           # HTML 템플릿
├── static/             # 정적 파일 (CSS, JS, 이미지)
├── uploads/            # 업로드된 파일
├── tests/              # 테스트 코드
├── config.py           # 설정 파일
├── run.py              # 애플리케이션 실행 파일
└── requirements.txt    # Python 의존성
```

## 개발 상태

현재 프로젝트 구조와 기본 환경 설정이 완료되었습니다. 다음 단계로 데이터베이스 모델과 사용자 인증 시스템을 구현할 예정입니다.

## 라이선스

MIT License