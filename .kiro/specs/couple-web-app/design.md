# 디자인 문서

## 개요

커플 웹 애플리케이션은 Python Flask 기반의 풀스택 웹 애플리케이션으로, 미니멀하고 직관적인 디자인을 통해 커플이 함께 사용할 수 있는 다양한 기능을 제공합니다. 로컬 환경에서 완전히 동작하며, 실시간 기능을 위해 WebSocket을 활용합니다.

## 아키텍처

### 전체 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (HTML/CSS/JS) │◄──►│   (Flask)       │◄──►│   (SQLite)      │
│   + SocketIO    │    │   + SocketIO    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  File Storage   │
                       │   (Local)       │
                       └─────────────────┘
```

### 기술 스택

**백엔드:**
- **Flask**: 경량 웹 프레임워크로 빠른 개발과 유연성 제공
- **Flask-SocketIO**: 실시간 양방향 통신을 위한 WebSocket 지원
- **SQLAlchemy**: ORM을 통한 데이터베이스 관리
- **SQLite**: 로컬 개발을 위한 경량 데이터베이스
- **Flask-Login**: 사용자 인증 및 세션 관리
- **Werkzeug**: 파일 업로드 및 보안 기능

**프론트엔드:**
- **HTML5**: 시맨틱 마크업
- **CSS3**: 미니멀 디자인과 반응형 레이아웃
- **Vanilla JavaScript**: 가벼운 클라이언트 사이드 로직
- **Socket.IO Client**: 실시간 통신

**개발 환경:**
- **Python 3.8+**: 가상환경(venv) 사용
- **로컬 파일 시스템**: 이미지 및 파일 저장

## 컴포넌트 및 인터페이스

### 1. 사용자 인증 시스템

**컴포넌트:**
- `AuthManager`: 사용자 등록, 로그인, 세션 관리
- `CoupleConnector`: 커플 연결 및 초대 코드 관리

**인터페이스:**
```python
class User:
    id: int
    email: str
    password_hash: str
    name: str
    partner_id: Optional[int]
    created_at: datetime

class CoupleConnection:
    id: int
    user1_id: int
    user2_id: int
    invite_code: str
    connected_at: datetime
```

### 2. D-Day 관리 시스템

**컴포넌트:**
- `DDayManager`: D-Day 생성, 수정, 삭제, 계산

**인터페이스:**
```python
class DDay:
    id: int
    couple_id: int
    title: str
    target_date: date
    description: Optional[str]
    created_by: int
    created_at: datetime
```

### 3. 캘린더 및 일정 시스템

**컴포넌트:**
- `CalendarManager`: 캘린더 뷰 생성 및 일정 관리
- `EventManager`: 일정 CRUD 및 참여자 관리

**인터페이스:**
```python
class Event:
    id: int
    couple_id: int
    title: str
    description: Optional[str]
    start_datetime: datetime
    end_datetime: datetime
    participant_type: str  # 'male', 'female', 'both'
    created_by: int
    created_at: datetime
```

### 4. 랜덤 질문 시스템

**컴포넌트:**
- `QuestionManager`: 질문 풀 관리 및 일일 질문 선택
- `AnswerManager`: 답변 저장 및 조회 권한 관리

**인터페이스:**
```python
class Question:
    id: int
    content: str
    category: str
    difficulty_level: int

class DailyQuestion:
    id: int
    couple_id: int
    question_id: int
    date: date
    user1_answered: bool
    user2_answered: bool

class Answer:
    id: int
    daily_question_id: int
    user_id: int
    content: str
    answered_at: datetime
```

### 5. 메모리 북 시스템

**컴포넌트:**
- `MemoryManager`: 추억 저장 및 조회
- `FileUploadManager`: 이미지 업로드 및 관리

**인터페이스:**
```python
class Memory:
    id: int
    couple_id: int
    title: str
    content: str
    memory_date: date
    image_path: Optional[str]
    created_by: int
    created_at: datetime
```

### 6. 무드 트래커 시스템

**컴포넌트:**
- `MoodTracker`: 기분 기록 및 히스토리 관리
- `MoodNotifier`: 실시간 기분 공유 알림

**인터페이스:**
```python
class MoodEntry:
    id: int
    user_id: int
    mood_level: int  # 1-5 scale
    note: Optional[str]
    date: date
    created_at: datetime
```

### 7. 실시간 알림 시스템

**컴포넌트:**
- `NotificationManager`: 알림 생성 및 전송
- `SocketIOHandler`: WebSocket 연결 및 이벤트 관리

**인터페이스:**
```python
class Notification:
    id: int
    user_id: int
    type: str  # 'mood_update', 'new_answer', 'event_reminder'
    title: str
    content: str
    is_read: bool
    created_at: datetime
```

## 데이터 모델

### 데이터베이스 스키마

```sql
-- 사용자 테이블
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    name VARCHAR(80) NOT NULL,
    partner_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (partner_id) REFERENCES users(id)
);

-- 커플 연결 테이블
CREATE TABLE couple_connections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user1_id INTEGER NOT NULL,
    user2_id INTEGER NOT NULL,
    invite_code VARCHAR(10) UNIQUE NOT NULL,
    connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user1_id) REFERENCES users(id),
    FOREIGN KEY (user2_id) REFERENCES users(id)
);

-- D-Day 테이블
CREATE TABLE ddays (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    couple_id INTEGER NOT NULL,
    title VARCHAR(100) NOT NULL,
    target_date DATE NOT NULL,
    description TEXT,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (couple_id) REFERENCES couple_connections(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- 이벤트 테이블
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    couple_id INTEGER NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    start_datetime TIMESTAMP NOT NULL,
    end_datetime TIMESTAMP NOT NULL,
    participant_type VARCHAR(10) NOT NULL CHECK (participant_type IN ('male', 'female', 'both')),
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (couple_id) REFERENCES couple_connections(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- 질문 풀 테이블
CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    category VARCHAR(50),
    difficulty_level INTEGER DEFAULT 1
);

-- 일일 질문 테이블
CREATE TABLE daily_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    couple_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    date DATE NOT NULL,
    user1_answered BOOLEAN DEFAULT FALSE,
    user2_answered BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (couple_id) REFERENCES couple_connections(id),
    FOREIGN KEY (question_id) REFERENCES questions(id),
    UNIQUE(couple_id, date)
);

-- 답변 테이블
CREATE TABLE answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    daily_question_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (daily_question_id) REFERENCES daily_questions(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(daily_question_id, user_id)
);

-- 메모리 테이블
CREATE TABLE memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    couple_id INTEGER NOT NULL,
    title VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    memory_date DATE NOT NULL,
    image_path VARCHAR(255),
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (couple_id) REFERENCES couple_connections(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- 무드 엔트리 테이블
CREATE TABLE mood_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    mood_level INTEGER NOT NULL CHECK (mood_level BETWEEN 1 AND 5),
    note TEXT,
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id, date)
);

-- 알림 테이블
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## 에러 핸들링

### 에러 처리 전략

1. **클라이언트 사이드 검증**
   - 폼 입력 실시간 검증
   - 사용자 친화적 에러 메시지
   - 네트워크 연결 상태 확인

2. **서버 사이드 검증**
   - 입력 데이터 유효성 검사
   - 권한 확인 (커플 관계 검증)
   - 데이터베이스 제약 조건 처리

3. **에러 응답 형식**
```python
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "입력 데이터가 올바르지 않습니다.",
        "details": {
            "field": "email",
            "reason": "이미 사용 중인 이메일입니다."
        }
    }
}
```

### 주요 에러 시나리오

- **인증 실패**: 잘못된 로그인 정보
- **권한 없음**: 다른 커플의 데이터 접근 시도
- **데이터 중복**: 이미 존재하는 D-Day나 일정
- **파일 업로드 실패**: 용량 초과 또는 지원하지 않는 형식
- **네트워크 오류**: WebSocket 연결 끊김

## 테스팅 전략

### 1. 단위 테스트 (Unit Tests)
- **모델 테스트**: 데이터 유효성 검사 및 관계 설정
- **서비스 로직 테스트**: 비즈니스 로직 검증
- **유틸리티 함수 테스트**: 날짜 계산, 파일 처리 등

### 2. 통합 테스트 (Integration Tests)
- **API 엔드포인트 테스트**: 요청/응답 검증
- **데이터베이스 연동 테스트**: CRUD 작업 검증
- **파일 업로드 테스트**: 이미지 저장 및 조회

### 3. 기능 테스트 (Functional Tests)
- **사용자 시나리오 테스트**: 회원가입부터 커플 연결까지
- **실시간 기능 테스트**: WebSocket 통신 검증
- **권한 테스트**: 다른 커플 데이터 접근 차단

### 4. 프론트엔드 테스트
- **UI 컴포넌트 테스트**: 폼 검증, 모달 동작
- **반응형 디자인 테스트**: 다양한 화면 크기 대응
- **브라우저 호환성 테스트**: 주요 브라우저 지원

### 테스트 도구
- **pytest**: Python 단위 테스트 및 통합 테스트
- **Flask-Testing**: Flask 애플리케이션 테스트 유틸리티
- **pytest-socketio**: SocketIO 테스트
- **Selenium**: 브라우저 자동화 테스트

## UI/UX 디자인 가이드라인

### 디자인 철학
- **미니멀리즘**: 불필요한 요소 제거, 핵심 기능에 집중
- **직관성**: 사용법을 배울 필요 없는 자연스러운 인터페이스
- **감성적 연결**: 커플의 감정적 유대감을 강화하는 디자인

### 색상 팔레트
```css
:root {
  /* Primary Colors - 부드럽고 따뜻한 톤 */
  --primary-pink: #F8BBD9;      /* 연한 핑크 - 여성 친화적 */
  --primary-blue: #B8E6E1;      /* 연한 민트 - 중성적이고 차분함 */
  --accent-coral: #FFB5A7;      /* 코랄 - 따뜻한 포인트 색상 */
  
  /* Neutral Colors - 미니멀한 배경 */
  --white: #FFFFFF;
  --light-gray: #F8F9FA;
  --medium-gray: #E9ECEF;
  --dark-gray: #6C757D;
  --charcoal: #343A40;
  
  /* Semantic Colors */
  --success: #28A745;
  --warning: #FFC107;
  --error: #DC3545;
  --info: #17A2B8;
}
```

### 타이포그래피
```css
/* Font Stack - 가독성과 감성을 고려한 폰트 */
--font-primary: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
--font-secondary: 'Noto Sans KR', sans-serif;

/* Font Sizes - 모바일 우선 반응형 */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
```

### 레이아웃 원칙
1. **모바일 우선**: 작은 화면에서 시작하여 확장
2. **카드 기반 레이아웃**: 각 기능을 독립적인 카드로 구성
3. **충분한 여백**: 시각적 휴식과 집중도 향상
4. **일관된 간격**: 8px 기반 그리드 시스템

### 인터랙션 디자인
- **부드러운 애니메이션**: 0.3초 이하의 자연스러운 전환
- **피드백 제공**: 모든 사용자 액션에 대한 즉각적 반응
- **로딩 상태**: 스켈레톤 UI 또는 스피너로 대기 시간 관리

### 반응형 브레이크포인트
```css
/* Mobile First Approach */
--mobile: 320px;
--tablet: 768px;
--desktop: 1024px;
--large: 1200px;
```

이 디자인 문서는 연구 결과를 바탕으로 Flask의 유연성과 SQLite의 간편함을 활용하여 로컬 환경에서 완전히 동작하는 커플 웹 애플리케이션을 구축하는 방향으로 설계되었습니다. 특히 여성 친화적이면서도 남성에게 부담스럽지 않은 미니멀한 디자인을 중심으로 사용자 경험을 최적화했습니다.