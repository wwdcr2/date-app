"""D-Day 모델"""

from datetime import datetime, date
from app.extensions import db

class DDay(db.Model):
    """D-Day 모델 클래스"""
    
    __tablename__ = 'ddays'
    
    id = db.Column(db.Integer, primary_key=True)
    couple_id = db.Column(db.Integer, db.ForeignKey('couple_connections.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    target_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def days_remaining(self):
        """남은 일수 계산 (음수면 지난 일수)"""
        today = date.today()
        delta = self.target_date - today
        return delta.days
    
    def is_past(self):
        """지난 날짜인지 확인"""
        return self.days_remaining() < 0
    
    def is_today(self):
        """오늘인지 확인"""
        return self.days_remaining() == 0
    
    def get_status_text(self):
        """상태 텍스트 반환"""
        days = self.days_remaining()
        if days > 0:
            return f"D-{days}"
        elif days == 0:
            return "D-Day"
        else:
            return f"D+{abs(days)}"
    
    def __repr__(self):
        return f'<DDay {self.title}>'