# 보안 기능 문서

## 개요

커플 웹 애플리케이션에 구현된 보안 기능들에 대한 상세 문서입니다. 이 문서는 구현된 보안 조치들과 사용 방법을 설명합니다.

## 구현된 보안 기능

### 1. 커플 관계 검증 미들웨어

#### 기능 설명
- 사용자가 커플로 연결된 상태에서만 특정 기능에 접근할 수 있도록 제한
- 다른 커플의 데이터에 접근하는 것을 방지

#### 구현 위치
- `app/utils/security.py` - `couple_relationship_required` 데코레이터
- `app/utils/security.py` - `validate_couple_access` 함수

#### 사용 방법
```python
from app.utils.security import couple_relationship_required

@app.route('/protected-route')
@login_required
@couple_relationship_required
def protected_function():
    # 커플 관계가 확인된 사용자만 접근 가능
    pass
```

#### 적용된 라우트
- 메모리 북 관련 모든 라우트
- 질문 관련 모든 라우트
- D-Day 관련 라우트
- 캘린더 관련 라우트
- 무드 트래커 관련 라우트

### 2. CSRF 보호

#### 기능 설명
- Cross-Site Request Forgery 공격 방지
- 모든 POST, PUT, DELETE 요청에 CSRF 토큰 검증

#### 구현 위치
- `app/extensions.py` - Flask-WTF CSRFProtect 초기화
- `config.py` - CSRF 관련 설정
- `templates/base.html` - CSRF 토큰 메타 태그

#### 설정
```python
# config.py
WTF_CSRF_ENABLED = True
WTF_CSRF_TIME_LIMIT = 3600  # 1시간
```

#### 템플릿에서 사용
```html
<!-- 메타 태그로 토큰 제공 -->
<meta name="csrf-token" content="{{ csrf_token() }}">

<!-- 폼에서 토큰 사용 -->
<form method="POST">
    {{ csrf_token() }}
    <!-- 폼 필드들 -->
</form>
```

### 3. 입력 데이터 검증 및 정제

#### 기능 설명
- 사용자 입력 데이터의 XSS 공격 방지
- HTML 태그 제거 및 특수 문자 이스케이프
- 입력 길이 제한

#### 구현 위치
- `app/utils/security.py` - `sanitize_input` 함수
- `app/utils/security.py` - `validate_form_data` 함수

#### 사용 방법
```python
from app.utils.security import sanitize_input, validate_form_data

# 입력 데이터 정제
clean_text = sanitize_input(user_input, max_length=100)

# 폼 데이터 검증
rules = {
    'title': {
        'required': True,
        'max_length': 100,
        'min_length': 2
    }
}
errors = validate_form_data(form_data, rules)
```

#### 정제 규칙
- HTML 태그 완전 제거
- 특수 문자 HTML 엔티티로 변환 (`<`, `>`, `&`, `"`, `'`)
- 앞뒤 공백 제거
- 최대 길이 제한

### 4. 파일 업로드 보안

#### 기능 설명
- 업로드 파일의 확장자, 크기, MIME 타입 검증
- 이미지 파일의 실제 형식 검증
- 악성 파일 업로드 방지

#### 구현 위치
- `app/utils/security.py` - `FileUploadValidator` 클래스

#### 보안 검증 항목
1. **파일 확장자 검증**: PNG, JPG, JPEG, GIF, WebP만 허용
2. **파일 크기 제한**: 최대 5MB
3. **MIME 타입 검증**: python-magic을 사용한 실제 파일 타입 확인
4. **이미지 검증**: PIL을 사용한 이미지 파일 유효성 검사
5. **이미지 크기 제한**: 최대 2048x2048 픽셀
6. **EXIF 데이터 제거**: 보안상 위험한 메타데이터 제거

#### 사용 방법
```python
from app.utils.security import FileUploadValidator

# 파일 검증 및 저장
filename, errors = FileUploadValidator.secure_save_file(file, upload_folder)
if errors:
    # 에러 처리
    for error in errors:
        flash(error, 'error')
else:
    # 성공적으로 저장됨
    pass
```

### 5. 악성 요청 탐지

#### 기능 설명
- SQL 인젝션 패턴 탐지
- XSS 공격 패턴 탐지
- 악성 요청 자동 차단

#### 구현 위치
- `app/utils/security.py` - `SecurityMiddleware` 클래스

#### 탐지 패턴
**SQL 인젝션 패턴:**
- `UNION SELECT`
- `SELECT FROM`
- `INSERT INTO`
- `DELETE FROM`
- `DROP TABLE`
- `UPDATE SET`

**XSS 패턴:**
- `<script>` 태그
- `javascript:` 프로토콜
- `on*=` 이벤트 핸들러
- `<iframe>` 태그

### 6. 보안 헤더

#### 기능 설명
- 브라우저 보안 기능 활성화
- 클릭재킹, MIME 스니핑 등 공격 방지

#### 적용된 헤더
```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Strict-Transport-Security: max-age=31536000; includeSubDomains (HTTPS 환경에서만)
```

### 7. 세션 보안

#### 기능 설명
- 안전한 세션 쿠키 설정
- 세션 하이재킹 방지

#### 설정
```python
# config.py
SESSION_COOKIE_SECURE = True  # HTTPS 환경에서만
SESSION_COOKIE_HTTPONLY = True  # JavaScript 접근 차단
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF 공격 방지
PERMANENT_SESSION_LIFETIME = 86400  # 24시간
```

## 보안 테스트

### 테스트 스크립트
보안 기능의 정상 작동을 확인하기 위한 테스트 스크립트가 제공됩니다.

```bash
# 보안 테스트 실행
python scripts/test_security.py
```

### 테스트 항목
1. **입력 데이터 정제 테스트**
   - XSS 패턴 제거 확인
   - HTML 태그 제거 확인
   - 특수 문자 이스케이프 확인

2. **폼 데이터 검증 테스트**
   - 필수 필드 검증
   - 길이 제한 검증
   - 패턴 매칭 검증

3. **파일 업로드 검증 테스트**
   - 허용된 파일 형식 확인
   - 파일 크기 제한 확인
   - 악성 파일 차단 확인

4. **악성 요청 탐지 테스트**
   - SQL 인젝션 패턴 탐지
   - XSS 패턴 탐지

## 보안 모범 사례

### 개발자 가이드라인

1. **입력 검증**
   - 모든 사용자 입력에 대해 `sanitize_input` 함수 사용
   - 폼 데이터는 `validate_form_data`로 검증
   - 파일 업로드는 `FileUploadValidator` 사용

2. **권한 검증**
   - 커플 관련 기능에는 `@couple_relationship_required` 데코레이터 사용
   - 리소스 접근 시 `validate_couple_access` 함수로 권한 확인

3. **CSRF 보호**
   - 모든 폼에 CSRF 토큰 포함
   - AJAX 요청 시 헤더에 CSRF 토큰 포함

4. **에러 처리**
   - 보안 관련 에러는 로그에 기록
   - 사용자에게는 일반적인 에러 메시지만 표시

### 배포 시 주의사항

1. **환경 설정**
   - `SECRET_KEY`를 강력한 랜덤 값으로 설정
   - `SESSION_COOKIE_SECURE=True` (HTTPS 환경)
   - `DEBUG=False` (프로덕션 환경)

2. **서버 설정**
   - HTTPS 사용 필수
   - 적절한 방화벽 설정
   - 정기적인 보안 업데이트

3. **모니터링**
   - 보안 로그 모니터링
   - 비정상적인 요청 패턴 감지
   - 정기적인 보안 스캔

## 알려진 제한사항

1. **python-magic 의존성**
   - 시스템에 libmagic이 설치되어 있어야 MIME 타입 검증이 완전히 작동
   - macOS에서는 `brew install libmagic` 필요

2. **파일 업로드 크기**
   - 현재 5MB로 제한되어 있음
   - 필요에 따라 `config.py`에서 조정 가능

3. **세션 저장소**
   - 현재 기본 Flask 세션 사용
   - 확장성을 위해서는 Redis 등 외부 저장소 고려

## 보안 업데이트 이력

### v1.0.0 (2025-01-19)
- 초기 보안 기능 구현
- CSRF 보호 추가
- 파일 업로드 보안 강화
- 입력 데이터 검증 및 정제
- 커플 관계 검증 미들웨어
- 악성 요청 탐지 시스템
- 보안 헤더 적용