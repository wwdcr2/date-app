"""쿼리 최적화 서비스"""

from datetime import datetime, date, timedelta
from sqlalchemy import and_, or_, func, desc, asc
from sqlalchemy.orm import joinedload, selectinload
from app.extensions import db
from app.models.user import User
from app.models.couple import CoupleConnection
from app.models.dday import DDay
from app.models.event import Event
from app.models.question import Question, DailyQuestion, Answer
from app.models.memory import Memory
from app.models.mood import MoodEntry
from app.models.notification import Notification

class OptimizedQueryService:
    """최적화된 쿼리를 제공하는 서비스 클래스"""
    
    @staticmethod
    def get_user_with_partner(user_id):
        """사용자와 파트너 정보를 한 번의 쿼리로 조회"""
        return User.query.options(
            joinedload(User.partner)
        ).get(user_id)
    
    @staticmethod
    def get_couple_connection_with_users(user_id):
        """커플 연결과 사용자 정보를 한 번의 쿼리로 조회"""
        return CoupleConnection.query.filter(
            or_(CoupleConnection.user1_id == user_id, 
                CoupleConnection.user2_id == user_id)
        ).first()
    
    @staticmethod
    def get_couple_ddays_optimized(couple_id, limit=None):
        """커플의 D-Day 목록을 최적화된 쿼리로 조회"""
        query = DDay.query.filter_by(couple_id=couple_id).options(
            joinedload(DDay.creator)
        ).order_by(DDay.target_date.asc())
        
        if limit:
            query = query.limit(limit)
            
        return query.all()
    
    @staticmethod
    def get_monthly_events_optimized(couple_id, year, month):
        """월별 이벤트를 최적화된 쿼리로 조회"""
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        return Event.query.filter(
            and_(
                Event.couple_id == couple_id,
                Event.start_datetime >= start_date,
                Event.start_datetime < end_date
            )
        ).options(
            joinedload(Event.creator)
        ).order_by(Event.start_datetime.asc()).all()
    
    @staticmethod
    def get_recent_answers_with_questions(user_id, limit=10):
        """사용자의 최근 답변을 질문과 함께 조회"""
        return Answer.query.filter_by(user_id=user_id).options(
            joinedload(Answer.question),
            joinedload(Answer.user)
        ).order_by(desc(Answer.date)).limit(limit).all()
    
    @staticmethod
    def get_daily_question_with_answers(couple_id, target_date):
        """특정 날짜의 일일 질문과 답변들을 한 번에 조회"""
        daily_question = DailyQuestion.query.filter_by(
            couple_id=couple_id,
            date=target_date
        ).options(
            joinedload(DailyQuestion.question)
        ).first()
        
        if not daily_question:
            return None
            
        # 해당 질문의 답변들도 함께 조회
        answers = Answer.query.filter_by(
            question_id=daily_question.question_id,
            date=target_date
        ).options(
            joinedload(Answer.user)
        ).all()
        
        return daily_question, answers
    
    @staticmethod
    def get_couple_memories_paginated(couple_id, page=1, per_page=10):
        """커플의 메모리를 페이지네이션으로 조회"""
        return Memory.query.filter_by(couple_id=couple_id).options(
            joinedload(Memory.creator)
        ).order_by(desc(Memory.memory_date)).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    @staticmethod
    def get_user_mood_statistics(user_id, start_date=None, end_date=None):
        """사용자의 기분 통계를 효율적으로 조회"""
        query = db.session.query(
            MoodEntry.mood_level,
            func.count(MoodEntry.id).label('count'),
            func.avg(MoodEntry.mood_level).label('average')
        ).filter_by(user_id=user_id)
        
        if start_date:
            query = query.filter(MoodEntry.date >= start_date)
        if end_date:
            query = query.filter(MoodEntry.date <= end_date)
            
        return query.group_by(MoodEntry.mood_level).all()
    
    @staticmethod
    def get_monthly_mood_data(user_id, year, month):
        """월별 기분 데이터를 효율적으로 조회"""
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)
        
        return MoodEntry.query.filter(
            and_(
                MoodEntry.user_id == user_id,
                MoodEntry.date >= start_date,
                MoodEntry.date < end_date
            )
        ).order_by(MoodEntry.date.asc()).all()
    
    @staticmethod
    def get_unread_notifications_count(user_id):
        """읽지 않은 알림 개수를 효율적으로 조회"""
        return db.session.query(func.count(Notification.id)).filter(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        ).scalar()
    
    @staticmethod
    def get_recent_notifications(user_id, limit=20):
        """최근 알림을 효율적으로 조회"""
        return Notification.query.filter_by(user_id=user_id).order_by(
            desc(Notification.created_at)
        ).limit(limit).all()
    
    @staticmethod
    def mark_notifications_as_read_bulk(user_id, notification_ids):
        """여러 알림을 한 번에 읽음 처리"""
        Notification.query.filter(
            and_(
                Notification.user_id == user_id,
                Notification.id.in_(notification_ids)
            )
        ).update({Notification.is_read: True}, synchronize_session=False)
        db.session.commit()
    
    @staticmethod
    def get_dashboard_data(user_id):
        """대시보드에 필요한 모든 데이터를 최적화된 쿼리로 조회"""
        # 커플 연결 정보
        couple_connection = OptimizedQueryService.get_couple_connection_with_users(user_id)
        
        if not couple_connection:
            return None
            
        # 최근 D-Day (상위 3개)
        recent_ddays = OptimizedQueryService.get_couple_ddays_optimized(
            couple_connection.id, limit=3
        )
        
        # 오늘의 이벤트
        today = datetime.now().date()
        today_events = Event.query.filter(
            and_(
                Event.couple_id == couple_connection.id,
                func.date(Event.start_datetime) == today
            )
        ).all()
        
        # 오늘의 질문
        today_question, today_answers = OptimizedQueryService.get_daily_question_with_answers(
            couple_connection.id, today
        )
        
        # 읽지 않은 알림 개수
        unread_count = OptimizedQueryService.get_unread_notifications_count(user_id)
        
        # 최근 메모리 (상위 3개)
        recent_memories = Memory.query.filter_by(
            couple_id=couple_connection.id
        ).order_by(desc(Memory.created_at)).limit(3).all()
        
        return {
            'couple_connection': couple_connection,
            'recent_ddays': recent_ddays,
            'today_events': today_events,
            'today_question': today_question,
            'today_answers': today_answers,
            'unread_notifications': unread_count,
            'recent_memories': recent_memories
        }
    
    @staticmethod
    def cleanup_old_notifications(days_old=30):
        """오래된 알림 정리 (배치 작업용)"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        deleted_count = Notification.query.filter(
            and_(
                Notification.created_at < cutoff_date,
                Notification.is_read == True
            )
        ).delete(synchronize_session=False)
        
        db.session.commit()
        return deleted_count
    
    @staticmethod
    def get_database_statistics():
        """데이터베이스 통계 정보 조회"""
        stats = {}
        
        try:
            # 각 테이블의 레코드 수
            stats['users'] = db.session.query(func.count(User.id)).scalar() or 0
            stats['couple_connections'] = db.session.query(func.count(CoupleConnection.id)).scalar() or 0
            stats['ddays'] = db.session.query(func.count(DDay.id)).scalar() or 0
            stats['events'] = db.session.query(func.count(Event.id)).scalar() or 0
            stats['questions'] = db.session.query(func.count(Question.id)).scalar() or 0
            stats['daily_questions'] = db.session.query(func.count(DailyQuestion.id)).scalar() or 0
            stats['answers'] = db.session.query(func.count(Answer.id)).scalar() or 0
            stats['memories'] = db.session.query(func.count(Memory.id)).scalar() or 0
            stats['mood_entries'] = db.session.query(func.count(MoodEntry.id)).scalar() or 0
            stats['notifications'] = db.session.query(func.count(Notification.id)).scalar() or 0
        except Exception as e:
            print(f"데이터베이스 통계 조회 중 오류: {e}")
            stats = {'error': str(e)}
        
        return stats