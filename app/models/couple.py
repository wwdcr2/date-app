"""커플 연결 모델"""

from datetime import datetime
import secrets
import string
from app.extensions import db

class CoupleConnection(db.Model):
    """커플 연결 모델 클래스"""
    
    __tablename__ = 'couple_connections'
    
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    invite_code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    connected_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계 설정
    ddays = db.relationship('DDay', backref='couple', lazy='dynamic')
    events = db.relationship('Event', backref='couple', lazy='dynamic')
    daily_questions = db.relationship('DailyQuestion', backref='couple', lazy='dynamic')
    memories = db.relationship('Memory', backref='couple', lazy='dynamic')
    
    @staticmethod
    def generate_invite_code():
        """고유한 초대 코드 생성"""
        while True:
            # 6자리 랜덤 코드 생성 (대문자 + 숫자)
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            
            # 중복 확인
            if not CoupleConnection.query.filter_by(invite_code=code).first():
                return code
    
    def get_users(self):
        """커플의 두 사용자 반환"""
        from app.models.user import User
        user1 = User.query.get(self.user1_id)
        user2 = User.query.get(self.user2_id)
        return user1, user2
    
    def get_partner_of(self, user_id):
        """특정 사용자의 파트너 반환"""
        from app.models.user import User
        if self.user1_id == user_id:
            return User.query.get(self.user2_id)
        elif self.user2_id == user_id:
            return User.query.get(self.user1_id)
        return None
    
    def __repr__(self):
        return f'<CoupleConnection {self.invite_code}>'