#!/usr/bin/env python3
"""
테스트용 서버 실행 스크립트
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.create_app import create_app

if __name__ == "__main__":
    app = create_app()
    
    print("🚀 테스트 서버 시작 중...")
    print("📍 URL: http://127.0.0.1:5003")
    print("🔗 Questions Daily: http://127.0.0.1:5003/questions/daily")
    print("🔗 Questions API: http://127.0.0.1:5003/questions/api/daily-question")
    print("\n⚠️  서버를 중지하려면 Ctrl+C를 누르세요")
    
    try:
        app.run(host='127.0.0.1', port=5003, debug=True, use_reloader=False)
    except KeyboardInterrupt:
        print("\n🛑 서버가 중지되었습니다.")