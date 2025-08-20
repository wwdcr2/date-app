"""알림 모델"""

from datetime import datetime
from app.extensions import db

class Notification(db.Model):
    """알림 모델 클래스"""
    
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def mark_as_read(self):
        """알림을 읽음으로 표시"""
        self.is_read = True
        db.session.commit()
    
    def get_type_icon(self):
        """알림 타입에 따른 아이콘 반환"""
        icon_map = {
            'mood_update': '😊',
            'new_answer': '💬',
            'event_reminder': '📅',
            'dday_reminder': '⏰',
            'new_memory': '📸',
            'partner_connected': '💕'
        }
        return icon_map.get(self.type, '🔔')
    
    def get_type_color(self):
        """알림 타입에 따른 색상 반환"""
        color_map = {
            'mood_update': '#F8BBD9',      # 핑크
            'new_answer': '#B8E6E1',       # 민트
            'event_reminder': '#FFB5A7',   # 코랄
            'dday_reminder': '#FFC107',    # 노란색
            'new_memory': '#28A745',       # 초록색
            'partner_connected': '#DC3545' # 빨간색
        }
        return color_map.get(self.type, '#6C757D')
    
    def get_formatted_time(self):
        """포맷된 시간 문자열 반환"""
        now = datetime.utcnow()
        diff = now - self.created_at
        
        if diff.days > 0:
            return f"{diff.days}일 전"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours}시간 전"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes}분 전"
        else:
            return "방금 전"
    
    @staticmethod
    def create_notification(user_id, notification_type, title, content):
        """새 알림 생성"""
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            content=content
        )
        db.session.add(notification)
        db.session.commit()
        return notification
    
    @staticmethod
    def get_unread_count(user_id):
        """읽지 않은 알림 개수 반환"""
        return Notification.query.filter_by(user_id=user_id, is_read=False).count()
    
    def __repr__(self):
        return f'<Notification {self.title}>'