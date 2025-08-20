# 테스트 문서

이 문서는 커플 웹 애플리케이션의 테스트 코드에 대한 설명입니다.

## 테스트 구조

### 테스트 파일 구성

```
tests/
├── conftest.py              # 테스트 설정 및 픽스처
├── test_basic.py           # 기본 모델 및 데이터베이스 테스트
├── test_api_basic.py       # 기본 API 테스트 (일부 구현)
├── test_models.py          # 상세 모델 테스트 (일부 구현)
├── test_api_integration.py # API 통합 테스트 (일부 구현)
├── test_user_scenarios.py  # 사용자 시나리오 테스트 (일부 구현)
├── run_tests.py            # 테스트 실행 스크립트
└── README.md               # 이 문서
```

## 구현된 테스트

### 1. 기본 모델 테스트 (`test_basic.py`)

#### TestBasicModels 클래스
- **test_user_creation_and_password**: 사용자 생성 및 비밀번호 해싱 테스트
- **test_dday_calculation**: D-Day 계산 로직 테스트 (미래/과거/오늘)
- **test_event_participant_colors**: 이벤트 참여자별 색상 테스트
- **test_mood_entry_emoji**: 무드 레벨별 이모지 테스트
- **test_question_creation**: 질문 생성 테스트
- **test_memory_creation**: 메모리 생성 테스트
- **test_notification_creation**: 알림 생성 테스트
- **test_couple_connection_invite_code**: 커플 연결 초대 코드 생성 테스트

#### TestDatabaseOperations 클래스
- **test_user_crud_operations**: 사용자 CRUD 작업 테스트
- **test_dday_crud_operations**: D-Day CRUD 작업 테스트

### 2. 테스트 설정 (`conftest.py`)

#### 주요 픽스처
- **app**: 테스트용 Flask 애플리케이션 생성
- **client**: 테스트 클라이언트
- **runner**: CLI 러너
- **test_user, test_partner, test_couple**: 테스트용 데이터 (ID만 반환)

#### 테스트 설정
- SQLite 인메모리 데이터베이스 사용
- CSRF 보호 비활성화
- 임시 업로드 폴더 설정
- 각 테스트마다 독립적인 데이터베이스 생성/삭제

## 테스트 실행 방법

### 1. 기본 실행
```bash
# 가상환경 활성화
source venv/bin/activate

# 모든 기본 테스트 실행
python -m pytest tests/test_basic.py -v

# 특정 테스트 클래스 실행
python -m pytest tests/test_basic.py::TestBasicModels -v

# 특정 테스트 메서드 실행
python -m pytest tests/test_basic.py::TestBasicModels::test_user_creation_and_password -v
```

### 2. 테스트 실행 스크립트 사용
```bash
# 가상환경 활성화
source venv/bin/activate

# 스크립트 실행
python tests/run_tests.py
```

### 3. 커버리지 포함 실행 (선택사항)
```bash
# pytest-cov 설치 (필요시)
pip install pytest-cov

# 커버리지와 함께 실행
python -m pytest tests/test_basic.py --cov=app --cov-report=html
```

## 테스트 결과

현재 구현된 테스트는 모두 통과합니다:

```
======================== 10 passed, 4 warnings in 1.24s ========================
```

### 경고 사항
- SQLAlchemy 2.0에서 `Query.get()` 메서드가 deprecated 되었다는 경고가 있습니다.
- 이는 기능에 영향을 주지 않으며, 향후 SQLAlchemy 업데이트 시 수정 예정입니다.

## 테스트 범위

### 현재 테스트 커버리지

#### ✅ 완전히 테스트된 기능
1. **사용자 모델**
   - 사용자 생성
   - 비밀번호 해싱 및 검증
   - CRUD 작업

2. **D-Day 모델**
   - 날짜 계산 로직
   - 상태 텍스트 생성
   - CRUD 작업

3. **이벤트 모델**
   - 참여자별 색상 매핑
   - 참여자 텍스트 변환

4. **무드 엔트리 모델**
   - 이모지 매핑
   - 레벨 검증

5. **기타 모델**
   - 질문, 메모리, 알림, 커플 연결 기본 생성

6. **데이터베이스 연결**
   - 기본 연결 테스트
   - CRUD 작업 검증

#### 🚧 부분적으로 구현된 테스트
1. **API 엔드포인트 테스트** (`test_api_basic.py`)
   - 보안 미들웨어 설정 문제로 일부 실패
   - 기본 애플리케이션 테스트는 통과

2. **상세 모델 테스트** (`test_models.py`)
   - SQLAlchemy 세션 관리 문제로 일부 실패
   - 기본 모델 생성 테스트는 통과

3. **사용자 시나리오 테스트** (`test_user_scenarios.py`)
   - 복잡한 워크플로우 테스트 구현됨
   - 세션 관리 문제로 실행 불가

## 향후 개선 사항

### 1. 우선순위 높음
- [ ] API 엔드포인트 테스트 수정 (보안 미들웨어 설정)
- [ ] SQLAlchemy 세션 관리 개선
- [ ] 인증 관련 테스트 완성

### 2. 우선순위 중간
- [ ] 실시간 기능 (SocketIO) 테스트
- [ ] 파일 업로드 테스트
- [ ] 성능 테스트

### 3. 우선순위 낮음
- [ ] E2E 테스트 (Selenium)
- [ ] 부하 테스트
- [ ] 보안 테스트 강화

## 테스트 작성 가이드라인

### 1. 테스트 명명 규칙
- 테스트 메서드: `test_기능_상황` (예: `test_user_creation_success`)
- 테스트 클래스: `Test기능명` (예: `TestUserModel`)

### 2. 테스트 구조
```python
def test_feature_scenario(self, app):
    """테스트 설명"""
    with app.app_context():
        # Given: 테스트 데이터 준비
        
        # When: 테스트 실행
        
        # Then: 결과 검증
        assert expected == actual
```

### 3. 픽스처 사용
- 공통 테스트 데이터는 `conftest.py`에 픽스처로 정의
- 각 테스트에서 필요한 데이터만 생성
- 테스트 간 독립성 보장

### 4. 에러 테스트
```python
def test_feature_error_case(self, app):
    """에러 케이스 테스트"""
    with app.app_context():
        with pytest.raises(ExpectedError):
            # 에러가 발생해야 하는 코드
            pass
```

## 문제 해결

### 자주 발생하는 문제

1. **SQLAlchemy DetachedInstanceError**
   - 원인: 서로 다른 세션에서 객체 접근
   - 해결: 각 테스트에서 필요한 데이터를 직접 생성

2. **Flask 애플리케이션 컨텍스트 오류**
   - 원인: 애플리케이션 컨텍스트 외부에서 데이터베이스 접근
   - 해결: `with app.app_context():` 사용

3. **테스트 데이터 격리 문제**
   - 원인: 테스트 간 데이터 공유
   - 해결: 각 테스트마다 새로운 데이터베이스 생성

### 디버깅 팁

1. **상세한 출력 보기**
   ```bash
   python -m pytest tests/test_basic.py -v -s
   ```

2. **특정 테스트만 실행**
   ```bash
   python -m pytest tests/test_basic.py::TestBasicModels::test_user_creation_and_password -v
   ```

3. **실패 시 즉시 중단**
   ```bash
   python -m pytest tests/test_basic.py -x
   ```

## 결론

현재 구현된 테스트는 애플리케이션의 핵심 기능들을 검증하며, 모든 기본 테스트가 성공적으로 통과합니다. 향후 API 테스트와 사용자 시나리오 테스트를 완성하면 더욱 견고한 테스트 스위트가 될 것입니다.