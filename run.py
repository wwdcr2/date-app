"""애플리케이션 실행 파일"""

import os
from app.create_app import create_app
from app.extensions import socketio

# Flask 애플리케이션 생성
app = create_app()

if __name__ == '__main__':
    # 개발 서버 실행
    socketio.run(app, 
                debug=True, 
                host='127.0.0.1', 
                port=5001,
                allow_unsafe_werkzeug=True)