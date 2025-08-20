"""사용자 모델"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class User(UserMixin, db.Model):
    """사용자 모델 클래스"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    partner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계 설정
    partner = db.relationship('User', remote_side=[id], backref='partner_of')
    
    # 커플 연결 관계 (사용자가 생성한 연결)
    created_connections = db.relationship('CoupleConnection', 
                                        foreign_keys='CoupleConnection.user1_id',
                                        backref='creator')
    
    # 커플 연결 관계 (사용자가 참여한 연결)
    joined_connections = db.relationship('CoupleConnection',
                                       foreign_keys='CoupleConnection.user2_id',
                                       backref='joiner')
    
    # D-Day 관계
    created_ddays = db.relationship('DDay', backref='creator', lazy='dynamic')
    
    # 이벤트 관계
    created_events = db.relationship('Event', backref='creator', lazy='dynamic')
    
    # 답변 관계
    answers = db.relationship('Answer', backref='user', lazy='dynamic')
    
    # 메모리 관계
    created_memories = db.relationship('Memory', backref='creator', lazy='dynamic')
    
    # 무드 엔트리 관계
    mood_entries = db.relationship('MoodEntry', backref='user', lazy='dynamic')
    
    # 알림 관계
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """비밀번호 해시 설정"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """비밀번호 확인"""
        return check_password_hash(self.password_hash, password)
    
    def get_couple_connection(self):
        """사용자의 커플 연결 정보 반환"""
        from app.models.couple import CoupleConnection
        connection = CoupleConnection.query.filter(
            (CoupleConnection.user1_id == self.id) | 
            (CoupleConnection.user2_id == self.id)
        ).first()
        return connection
    
    def get_partner(self):
        """파트너 사용자 객체 반환"""
        connection = self.get_couple_connection()
        if connection:
            partner_id = connection.user2_id if connection.user1_id == self.id else connection.user1_id
            return User.query.get(partner_id)
        return None
    
    def is_connected_to_partner(self):
        """파트너와 연결되어 있는지 확인"""
        return self.get_couple_connection() is not None
    
    def __repr__(self):
        return f'<User {self.email}>'