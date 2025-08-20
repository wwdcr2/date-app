"""무드(기분) 모델"""

from datetime import datetime, date
from app.extensions import db

class MoodEntry(db.Model):
    """무드 엔트리 모델 클래스"""
    
    __tablename__ = 'mood_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mood_level = db.Column(db.Integer, nullable=False)  # 1-5 scale
    note = db.Column(db.Text)
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 체크 제약 조건 및 유니크 제약 조건
    __table_args__ = (
        db.CheckConstraint(mood_level.between(1, 5), name='check_mood_level'),
        db.UniqueConstraint('user_id', 'date', name='unique_user_date_mood'),
    )
    
    def get_mood_emoji(self):
        """기분 레벨에 따른 이모지 반환"""
        emoji_map = {
            1: '😢',  # 매우 나쁨
            2: '😞',  # 나쁨
            3: '😐',  # 보통
            4: '😊',  # 좋음
            5: '😍'   # 매우 좋음
        }
        return emoji_map.get(self.mood_level, '😐')
    
    def get_mood_text(self):
        """기분 레벨에 따른 텍스트 반환"""
        text_map = {
            1: '매우 나쁨',
            2: '나쁨',
            3: '보통',
            4: '좋음',
            5: '매우 좋음'
        }
        return text_map.get(self.mood_level, '보통')
    
    def get_mood_color(self):
        """기분 레벨에 따른 색상 반환"""
        color_map = {
            1: '#DC3545',  # 빨간색 (매우 나쁨)
            2: '#FFC107',  # 노란색 (나쁨)
            3: '#6C757D',  # 회색 (보통)
            4: '#28A745',  # 초록색 (좋음)
            5: '#F8BBD9'   # 핑크색 (매우 좋음)
        }
        return color_map.get(self.mood_level, '#6C757D')
    
    @staticmethod
    def get_mood_statistics(user_id, start_date=None, end_date=None):
        """사용자의 기분 통계 반환"""
        query = MoodEntry.query.filter_by(user_id=user_id)
        
        if start_date:
            query = query.filter(MoodEntry.date >= start_date)
        if end_date:
            query = query.filter(MoodEntry.date <= end_date)
        
        entries = query.all()
        
        if not entries:
            return {
                'average': 0,
                'total_entries': 0,
                'mood_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            }
        
        total_mood = sum(entry.mood_level for entry in entries)
        average_mood = total_mood / len(entries)
        
        mood_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for entry in entries:
            mood_distribution[entry.mood_level] += 1
        
        return {
            'average': round(average_mood, 2),
            'total_entries': len(entries),
            'mood_distribution': mood_distribution
        }
    
    def __repr__(self):
        return f'<MoodEntry {self.date}: {self.get_mood_emoji()}>'