"""질문 관련 모델"""

from datetime import datetime, date
from app.extensions import db

class Question(db.Model):
    """질문 풀 모델 클래스"""
    
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)  # content -> text로 변경
    category = db.Column(db.String(50))
    difficulty = db.Column(db.String(20), default='easy')  # difficulty_level -> difficulty로 변경
    
    # 관계 설정
    daily_questions = db.relationship('DailyQuestion', backref='question', lazy='dynamic')
    
    def __repr__(self):
        return f'<Question {self.id}: {self.text[:50]}...>'

class DailyQuestion(db.Model):
    """일일 질문 모델 클래스 - 커플별 일일 질문 할당 추적용"""
    
    __tablename__ = 'daily_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    couple_id = db.Column(db.Integer, db.ForeignKey('couple_connections.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    
    # 유니크 제약 조건 - 한 커플은 하루에 하나의 질문만
    __table_args__ = (
        db.UniqueConstraint('couple_id', 'date', name='unique_couple_date'),
    )
    
    # 관계 설정은 CoupleConnection에서 정의됨
    
    def get_answer_status(self):
        """커플의 답변 상태 반환"""
        from app.models.couple import CoupleConnection
        connection = CoupleConnection.query.get(self.couple_id)
        
        if not connection:
            return {
                'user1_answered': False,
                'user2_answered': False,
                'both_answered': False,
                'user1_answer': None,
                'user2_answer': None
            }
        
        return Answer.get_answer_completion_status(
            self.question_id, 
            self.date, 
            connection.user1_id, 
            connection.user2_id
        )
    
    def can_user_view_partner_answer(self, user_id):
        """사용자가 파트너의 답변을 볼 수 있는지 확인"""
        # 자신이 답변한 경우에만 파트너 답변 조회 가능
        user_answer = Answer.query.filter_by(
            question_id=self.question_id,
            user_id=user_id,
            date=self.date
        ).first()
        
        return user_answer is not None
    
    def get_user_answer(self, user_id):
        """특정 사용자의 답변 반환"""
        return Answer.query.filter_by(
            question_id=self.question_id,
            user_id=user_id,
            date=self.date
        ).first()
    
    def get_partner_answer(self, user_id):
        """파트너의 답변 반환 (접근 권한 확인 후)"""
        if not self.can_user_view_partner_answer(user_id):
            return None
            
        from app.models.couple import CoupleConnection
        connection = CoupleConnection.query.get(self.couple_id)
        
        if not connection:
            return None
            
        # 파트너 ID 찾기
        partner_id = connection.user2_id if connection.user1_id == user_id else connection.user1_id
        
        return Answer.query.filter_by(
            question_id=self.question_id,
            user_id=partner_id,
            date=self.date
        ).first()
    
    def __repr__(self):
        return f'<DailyQuestion {self.date}: {self.question.text[:30]}...>'

class Answer(db.Model):
    """답변 모델 클래스"""
    
    __tablename__ = 'answers'
    
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    answer_text = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 유니크 제약 조건 (한 사용자는 하루에 하나의 질문에 하나의 답변만)
    __table_args__ = (
        db.UniqueConstraint('question_id', 'user_id', 'date', name='unique_user_question_date'),
    )
    
    # 관계 설정
    question = db.relationship('Question', backref='question_answers')
    
    def can_view_partner_answer(self, partner_id):
        """파트너의 답변을 볼 수 있는지 확인 (자신이 답변한 경우에만)"""
        # 같은 날짜, 같은 질문에 대한 파트너의 답변이 있는지 확인
        partner_answer = Answer.query.filter_by(
            question_id=self.question_id,
            user_id=partner_id,
            date=self.date
        ).first()
        
        return partner_answer is not None
    
    def get_partner_answer(self, partner_id):
        """파트너의 답변 반환 (접근 권한이 있는 경우에만)"""
        if not self.can_view_partner_answer(partner_id):
            return None
            
        return Answer.query.filter_by(
            question_id=self.question_id,
            user_id=partner_id,
            date=self.date
        ).first()
    
    @staticmethod
    def get_answer_completion_status(question_id, date, user1_id, user2_id):
        """특정 질문에 대한 두 사용자의 답변 완료 상태 반환"""
        user1_answer = Answer.query.filter_by(
            question_id=question_id,
            user_id=user1_id,
            date=date
        ).first()
        
        user2_answer = Answer.query.filter_by(
            question_id=question_id,
            user_id=user2_id,
            date=date
        ).first()
        
        return {
            'user1_answered': user1_answer is not None,
            'user2_answered': user2_answer is not None,
            'both_answered': user1_answer is not None and user2_answer is not None,
            'user1_answer': user1_answer,
            'user2_answer': user2_answer
        }
    
    def __repr__(self):
        return f'<Answer {self.id}: {self.answer_text[:30]}...>'