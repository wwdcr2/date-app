"""메모리(추억) 모델"""

from datetime import datetime
import os
from app.extensions import db

class Memory(db.Model):
    """메모리(추억) 모델 클래스"""
    
    __tablename__ = 'memories'
    
    id = db.Column(db.Integer, primary_key=True)
    couple_id = db.Column(db.Integer, db.ForeignKey('couple_connections.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    memory_date = db.Column(db.Date, nullable=False)
    image_path = db.Column(db.String(255))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def has_image(self):
        """이미지가 있는지 확인"""
        return self.image_path is not None and self.image_path.strip() != ''
    
    def get_image_url(self):
        """이미지 URL 반환"""
        if self.has_image():
            return f'/uploads/{self.image_path}'
        return None
    
    def get_image_full_path(self):
        """이미지 전체 경로 반환"""
        if self.has_image():
            from flask import current_app
            return os.path.join(current_app.config['UPLOAD_FOLDER'], self.image_path)
        return None
    
    def delete_image(self):
        """이미지 파일 삭제"""
        if self.has_image():
            image_path = self.get_image_full_path()
            if image_path and os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    return True
                except OSError:
                    return False
        return True
    
    def get_formatted_date(self):
        """포맷된 날짜 문자열 반환"""
        return self.memory_date.strftime('%Y년 %m월 %d일')
    
    def __repr__(self):
        return f'<Memory {self.title}>'