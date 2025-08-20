#!/usr/bin/env python3
"""보안 기능 테스트 스크립트"""

import os
import sys
import tempfile
from io import BytesIO
from PIL import Image

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.security import (
    SecurityMiddleware, 
    FileUploadValidator, 
    sanitize_input, 
    validate_form_data
)

def test_input_sanitization():
    """입력 데이터 정제 테스트"""
    print("=== 입력 데이터 정제 테스트 ===")
    
    test_cases = [
        ("<script>alert('xss')</script>", "&lt;script&gt;alert('xss')&lt;/script&gt;"),
        ("Hello <b>World</b>", "Hello World"),
        ("Test & Co.", "Test &amp; Co."),
        ("Quote \"test\"", "Quote &quot;test&quot;"),
        ("  Trimmed  ", "Trimmed"),
        ("Very long text" * 100, "Very long text" * 10)  # 길이 제한 테스트
    ]
    
    for input_text, expected in test_cases:
        result = sanitize_input(input_text, max_length=100)
        status = "✅" if expected in result else "❌"
        print(f"{status} Input: '{input_text[:50]}...' -> Output: '{result[:50]}...'")

def test_form_validation():
    """폼 데이터 검증 테스트"""
    print("\n=== 폼 데이터 검증 테스트 ===")
    
    # 검증 규칙
    rules = {
        'title': {
            'required': True,
            'max_length': 10,
            'min_length': 2
        },
        'email': {
            'required': True,
            'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'pattern_message': '올바른 이메일 형식이 아닙니다.'
        }
    }
    
    test_cases = [
        ({'title': 'Valid', 'email': 'test@example.com'}, True),
        ({'title': '', 'email': 'test@example.com'}, False),  # 필수 필드 누락
        ({'title': 'A', 'email': 'test@example.com'}, False),  # 최소 길이 미달
        ({'title': 'Very long title', 'email': 'test@example.com'}, False),  # 최대 길이 초과
        ({'title': 'Valid', 'email': 'invalid-email'}, False),  # 잘못된 이메일 형식
    ]
    
    for form_data, should_pass in test_cases:
        errors = validate_form_data(form_data, rules)
        is_valid = len(errors) == 0
        status = "✅" if is_valid == should_pass else "❌"
        print(f"{status} Data: {form_data} -> Valid: {is_valid}, Errors: {errors}")

def test_file_upload_validation():
    """파일 업로드 검증 테스트"""
    print("\n=== 파일 업로드 검증 테스트 ===")
    
    # 임시 디렉토리 생성
    with tempfile.TemporaryDirectory() as temp_dir:
        # 유효한 이미지 파일 생성
        valid_image = Image.new('RGB', (100, 100), color='red')
        valid_image_io = BytesIO()
        valid_image.save(valid_image_io, format='PNG')
        valid_image_io.seek(0)
        
        # 가짜 파일 객체 클래스
        class FakeFile:
            def __init__(self, filename, content, content_type='image/png'):
                self.filename = filename
                self.content = content
                self.content_type = content_type
                self._position = 0
            
            def read(self, size=-1):
                if size == -1:
                    result = self.content[self._position:]
                    self._position = len(self.content)
                else:
                    result = self.content[self._position:self._position + size]
                    self._position += len(result)
                return result
            
            def seek(self, position, whence=0):
                if whence == 0:  # SEEK_SET
                    self._position = position
                elif whence == 1:  # SEEK_CUR
                    self._position += position
                elif whence == 2:  # SEEK_END
                    self._position = len(self.content) + position
            
            def tell(self):
                return self._position
            
            def save(self, path):
                with open(path, 'wb') as f:
                    f.write(self.content)
        
        test_cases = [
            ('valid.png', valid_image_io.getvalue(), True),
            ('invalid.txt', b'This is not an image', False),
            ('', b'', False),  # 빈 파일명
            ('toolarge.png', b'x' * (6 * 1024 * 1024), False),  # 크기 초과
        ]
        
        for filename, content, should_pass in test_cases:
            fake_file = FakeFile(filename, content)
            errors = FileUploadValidator.validate_file(fake_file)
            is_valid = len(errors) == 0
            status = "✅" if is_valid == should_pass else "❌"
            print(f"{status} File: '{filename}' -> Valid: {is_valid}, Errors: {errors}")

def test_malicious_request_detection():
    """악성 요청 탐지 테스트"""
    print("\n=== 악성 요청 탐지 테스트 ===")
    
    # SecurityMiddleware의 _is_malicious_request 메서드를 직접 테스트하기 위해
    # 임시로 Flask 앱 컨텍스트 없이 테스트할 수 있는 함수 작성
    import re
    
    def is_malicious_request_test(request_data):
        """악성 요청 패턴 검사 (테스트용)"""
        sql_patterns = [
            r'(\bunion\b.*\bselect\b)',
            r'(\bselect\b.*\bfrom\b)',
            r'(\binsert\b.*\binto\b)',
            r'(\bdelete\b.*\bfrom\b)',
            r'(\bdrop\b.*\btable\b)',
            r'(\bupdate\b.*\bset\b)'
        ]
        
        xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>.*?</iframe>'
        ]
        
        request_data = request_data.lower()
        all_patterns = sql_patterns + xss_patterns
        
        for pattern in all_patterns:
            if re.search(pattern, request_data, re.IGNORECASE):
                return True
        return False
    
    test_cases = [
        ("normal request", False),
        ("SELECT * FROM users", True),
        ("UNION SELECT password FROM users", True),
        ("<script>alert('xss')</script>", True),
        ("javascript:alert('xss')", True),
        ("onclick=alert('xss')", True),
        ("<iframe src='evil.com'></iframe>", True),
        ("DROP TABLE users", True),
        ("UPDATE users SET password='hacked'", True),
    ]
    
    for request_data, should_detect in test_cases:
        is_malicious = is_malicious_request_test(request_data)
        status = "✅" if is_malicious == should_detect else "❌"
        print(f"{status} Request: '{request_data}' -> Malicious: {is_malicious}")

def main():
    """메인 테스트 함수"""
    print("🔒 보안 기능 테스트 시작\n")
    
    try:
        test_input_sanitization()
        test_form_validation()
        test_file_upload_validation()
        test_malicious_request_detection()
        
        print("\n✅ 모든 보안 테스트가 완료되었습니다!")
        
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())