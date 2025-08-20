"""SocketIO 이벤트 핸들러"""

from flask import request
from flask_login import current_user
from flask_socketio import emit, join_room, leave_room, disconnect
from app.extensions import socketio, db
from app.models.notification import Notification
import logging

# 연결된 사용자들을 추적하기 위한 딕셔너리
connected_users = {}

@socketio.on('connect')
def handle_connect():
    """클라이언트 연결 시 처리"""
    if current_user.is_authenticated:
        user_id = current_user.id
        session_id = request.sid
        
        # 사용자를 개인 룸에 추가
        join_room(f'user_{user_id}')
        
        # 연결된 사용자 추적
        connected_users[session_id] = user_id
        
        # 파트너가 온라인인지 확인
        partner = current_user.get_partner()
        if partner:
            partner_online = any(uid == partner.id for uid in connected_users.values())
            
            # 파트너에게 온라인 상태 알림
            emit('partner_status', {
                'partner_id': current_user.id,
                'partner_name': current_user.name,
                'status': 'online'
            }, room=f'user_{partner.id}')
            
            # 현재 사용자에게 파트너 상태 알림
            emit('partner_status', {
                'partner_id': partner.id,
                'partner_name': partner.name,
                'status': 'online' if partner_online else 'offline'
            })
        
        # 읽지 않은 알림 개수 전송
        unread_count = Notification.get_unread_count(user_id)
        emit('notification_count', {'count': unread_count})
        
        logging.info(f'User {current_user.name} (ID: {user_id}) connected')
        
    else:
        # 인증되지 않은 사용자는 연결 해제
        disconnect()

@socketio.on('disconnect')
def handle_disconnect():
    """클라이언트 연결 해제 시 처리"""
    session_id = request.sid
    
    if session_id in connected_users:
        user_id = connected_users[session_id]
        
        # 사용자 정보 가져오기
        from app.models.user import User
        user = User.query.get(user_id)
        
        if user:
            # 개인 룸에서 제거
            leave_room(f'user_{user_id}')
            
            # 파트너에게 오프라인 상태 알림
            partner = user.get_partner()
            if partner:
                emit('partner_status', {
                    'partner_id': user_id,
                    'partner_name': user.name,
                    'status': 'offline'
                }, room=f'user_{partner.id}')
            
            logging.info(f'User {user.name} (ID: {user_id}) disconnected')
        
        # 연결된 사용자 목록에서 제거
        del connected_users[session_id]

@socketio.on('join_couple_room')
def handle_join_couple_room():
    """커플 룸 참여"""
    if current_user.is_authenticated:
        connection = current_user.get_couple_connection()
        if connection:
            couple_room = f'couple_{connection.id}'
            join_room(couple_room)
            emit('joined_couple_room', {'room': couple_room})

@socketio.on('leave_couple_room')
def handle_leave_couple_room():
    """커플 룸 나가기"""
    if current_user.is_authenticated:
        connection = current_user.get_couple_connection()
        if connection:
            couple_room = f'couple_{connection.id}'
            leave_room(couple_room)
            emit('left_couple_room', {'room': couple_room})

@socketio.on('mark_notification_read')
def handle_mark_notification_read(data):
    """알림을 읽음으로 표시"""
    if current_user.is_authenticated:
        notification_id = data.get('notification_id')
        if notification_id:
            notification = Notification.query.filter_by(
                id=notification_id,
                user_id=current_user.id
            ).first()
            
            if notification and not notification.is_read:
                notification.mark_as_read()
                
                # 업데이트된 읽지 않은 알림 개수 전송
                unread_count = Notification.get_unread_count(current_user.id)
                emit('notification_count', {'count': unread_count})
                
                emit('notification_marked_read', {
                    'notification_id': notification_id,
                    'success': True
                })

@socketio.on('get_notifications')
def handle_get_notifications():
    """최근 알림 목록 가져오기"""
    if current_user.is_authenticated:
        notifications = Notification.query.filter_by(user_id=current_user.id)\
                                        .order_by(Notification.created_at.desc())\
                                        .limit(10).all()
        
        notification_data = [{
            'id': notif.id,
            'type': notif.type,
            'title': notif.title,
            'content': notif.content,
            'icon': notif.get_type_icon(),
            'color': notif.get_type_color(),
            'is_read': notif.is_read,
            'formatted_time': notif.get_formatted_time(),
            'created_at': notif.created_at.isoformat()
        } for notif in notifications]
        
        emit('notifications_list', {'notifications': notification_data})

def send_notification_to_user(user_id, notification_type, title, content, data=None):
    """특정 사용자에게 실시간 알림 전송"""
    try:
        # 데이터베이스에 알림 저장
        notification = Notification.create_notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            content=content
        )
        
        # 실시간 알림 전송
        notification_data = {
            'id': notification.id,
            'type': notification.type,
            'title': notification.title,
            'content': notification.content,
            'icon': notification.get_type_icon(),
            'color': notification.get_type_color(),
            'formatted_time': notification.get_formatted_time(),
            'created_at': notification.created_at.isoformat()
        }
        
        # 추가 데이터가 있으면 포함
        if data:
            notification_data.update(data)
        
        # 사용자의 개인 룸으로 알림 전송
        socketio.emit('new_notification', notification_data, room=f'user_{user_id}')
        
        # 읽지 않은 알림 개수 업데이트
        unread_count = Notification.get_unread_count(user_id)
        socketio.emit('notification_count', {'count': unread_count}, room=f'user_{user_id}')
        
        logging.info(f'Notification sent to user {user_id}: {title}')
        return notification
        
    except Exception as e:
        logging.error(f'Failed to send notification to user {user_id}: {str(e)}')
        return None

def send_notification_to_couple(couple_id, notification_type, title, content, exclude_user_id=None, data=None):
    """커플 모두에게 실시간 알림 전송"""
    try:
        from app.models.couple import CoupleConnection
        
        connection = CoupleConnection.query.get(couple_id)
        if not connection:
            return
        
        # 커플의 두 사용자에게 알림 전송
        user_ids = [connection.user1_id, connection.user2_id]
        
        for user_id in user_ids:
            if exclude_user_id and user_id == exclude_user_id:
                continue
            
            send_notification_to_user(user_id, notification_type, title, content, data)
        
        logging.info(f'Notification sent to couple {couple_id}: {title}')
        
    except Exception as e:
        logging.error(f'Failed to send notification to couple {couple_id}: {str(e)}')

def notify_mood_update(user_id, mood_level, mood_emoji, mood_text):
    """기분 업데이트 알림"""
    from app.models.user import User
    
    user = User.query.get(user_id)
    if not user:
        return
    
    partner = user.get_partner()
    if not partner:
        return
    
    title = f"{user.name}님이 기분을 기록했습니다"
    content = f"오늘의 기분: {mood_emoji} {mood_text}"
    
    send_notification_to_user(
        partner.id,
        'mood_update',
        title,
        content,
        data={
            'mood_level': mood_level,
            'mood_emoji': mood_emoji,
            'mood_text': mood_text,
            'user_name': user.name
        }
    )

def notify_new_answer(user_id, question_text):
    """새로운 답변 알림"""
    from app.models.user import User
    
    user = User.query.get(user_id)
    if not user:
        return
    
    partner = user.get_partner()
    if not partner:
        return
    
    title = f"{user.name}님이 질문에 답변했습니다"
    content = f"질문: {question_text[:50]}{'...' if len(question_text) > 50 else ''}"
    
    send_notification_to_user(
        partner.id,
        'new_answer',
        title,
        content,
        data={
            'question_text': question_text,
            'user_name': user.name
        }
    )

def notify_new_memory(user_id, memory_title):
    """새로운 추억 알림"""
    from app.models.user import User
    
    user = User.query.get(user_id)
    if not user:
        return
    
    partner = user.get_partner()
    if not partner:
        return
    
    title = f"{user.name}님이 새로운 추억을 추가했습니다"
    content = f"추억: {memory_title}"
    
    send_notification_to_user(
        partner.id,
        'new_memory',
        title,
        content,
        data={
            'memory_title': memory_title,
            'user_name': user.name
        }
    )

def notify_event_reminder(user_id, event_title, event_time):
    """일정 알림"""
    title = "일정 알림"
    content = f"{event_title} - {event_time}"
    
    send_notification_to_user(
        user_id,
        'event_reminder',
        title,
        content,
        data={
            'event_title': event_title,
            'event_time': event_time
        }
    )