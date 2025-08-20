"""이벤트(일정) 모델"""

from datetime import datetime
from app.extensions import db

class Event(db.Model):
    """이벤트(일정) 모델 클래스"""
    
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    couple_id = db.Column(db.Integer, db.ForeignKey('couple_connections.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    participant_type = db.Column(db.String(10), nullable=False)  # 'male', 'female', 'both'
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 체크 제약 조건
    __table_args__ = (
        db.CheckConstraint(participant_type.in_(['male', 'female', 'both']), 
                          name='check_participant_type'),
    )
    
    def get_participant_color(self):
        """참여자 타입에 따른 색상 반환"""
        color_map = {
            'male': '#B8E6E1',      # 연한 민트 (남성)
            'female': '#F8BBD9',    # 연한 핑크 (여성)
            'both': '#FFB5A7'       # 코랄 (함께)
        }
        return color_map.get(self.participant_type, '#E9ECEF')
    
    def get_participant_text(self):
        """참여자 타입 텍스트 반환"""
        text_map = {
            'male': '남자',
            'female': '여자',
            'both': '함께'
        }
        return text_map.get(self.participant_type, '알 수 없음')
    
    def is_all_day(self):
        """하루 종일 이벤트인지 확인"""
        return (self.end_datetime - self.start_datetime).days >= 1 and \
               self.start_datetime.time() == self.end_datetime.time()
    
    def get_duration_text(self):
        """이벤트 기간 텍스트 반환"""
        if self.is_all_day():
            if self.start_datetime.date() == self.end_datetime.date():
                return "하루 종일"
            else:
                days = (self.end_datetime.date() - self.start_datetime.date()).days
                return f"{days}일간"
        else:
            duration = self.end_datetime - self.start_datetime
            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60
            if hours > 0:
                return f"{hours}시간 {minutes}분" if minutes > 0 else f"{hours}시간"
            else:
                return f"{minutes}분"
    
    def __repr__(self):
        return f'<Event {self.title}>'