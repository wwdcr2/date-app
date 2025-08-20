#!/usr/bin/env python3
"""테스트 실행 스크립트"""

import subprocess
import sys
import os

def run_command(command, description):
    """명령어 실행 및 결과 출력"""
    print(f"\n{'='*60}")
    print(f"실행 중: {description}")
    print(f"명령어: {command}")
    print('='*60)
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print("STDOUT:")
        print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    print(f"종료 코드: {result.returncode}")
    return result.returncode == 0

def main():
    """메인 테스트 실행 함수"""
    # 가상환경 활성화 확인
    if not os.environ.get('VIRTUAL_ENV'):
        print("경고: 가상환경이 활성화되지 않았습니다.")
        print("다음 명령어로 가상환경을 활성화하세요: source venv/bin/activate")
    
    # 테스트 실행
    tests = [
        ("python -m pytest tests/test_basic.py -v", "기본 모델 및 데이터베이스 테스트"),
        ("python -m pytest tests/test_basic.py::TestBasicModels -v", "모델 단위 테스트"),
        ("python -m pytest tests/test_basic.py::TestDatabaseOperations -v", "데이터베이스 CRUD 테스트"),
    ]
    
    success_count = 0
    total_count = len(tests)
    
    for command, description in tests:
        if run_command(command, description):
            success_count += 1
            print(f"✅ {description} - 성공")
        else:
            print(f"❌ {description} - 실패")
    
    # 결과 요약
    print(f"\n{'='*60}")
    print("테스트 결과 요약")
    print('='*60)
    print(f"총 테스트 그룹: {total_count}")
    print(f"성공: {success_count}")
    print(f"실패: {total_count - success_count}")
    
    if success_count == total_count:
        print("🎉 모든 테스트가 성공했습니다!")
        return 0
    else:
        print("⚠️  일부 테스트가 실패했습니다.")
        return 1

if __name__ == "__main__":
    sys.exit(main())