"""알림 관련 라우트"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from app.extensions import db
from app.models.notification import Notification

# 블루프린트 생성
notifications_bp = Blueprint('notifications', __name__, url_prefix='/notifications')

@notifications_bp.route('/')
@login_required
def index():
    """알림 목록 페이지"""
    # 페이지네이션
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # 필터
    filter_type = request.args.get('type')
    show_read = request.args.get('show_read', 'false') == 'true'
    
    # 쿼리 구성
    query = Notification.query.filter_by(user_id=current_user.id)
    
    if filter_type:
        query = query.filter(Notification.type == filter_type)
    
    if not show_read:
        query = query.filter(Notification.is_read == False)
    
    notifications = query.order_by(Notification.created_at.desc())\
                         .paginate(page=page, per_page=per_page, error_out=False)
    
    # 알림 타입 목록
    notification_types = db.session.query(Notification.type)\
                                  .filter_by(user_id=current_user.id)\
                                  .distinct().all()
    notification_types = [t[0] for t in notification_types]
    
    return render_template('notifications/index.html',
                         notifications=notifications,
                         notification_types=notification_types,
                         current_filter=filter_type,
                         show_read=show_read)

@notifications_bp.route('/mark-read/<int:notification_id>', methods=['POST'])
@login_required
def mark_read(notification_id):
    """알림을 읽음으로 표시"""
    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=current_user.id
    ).first_or_404()
    
    if not notification.is_read:
        notification.mark_as_read()
    
    return jsonify({'success': True})

@notifications_bp.route('/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    """모든 알림을 읽음으로 표시"""
    notifications = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).all()
    
    for notification in notifications:
        notification.is_read = True
    
    db.session.commit()
    
    return jsonify({'success': True, 'count': len(notifications)})

@notifications_bp.route('/delete/<int:notification_id>', methods=['POST'])
@login_required
def delete(notification_id):
    """알림 삭제"""
    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=current_user.id
    ).first_or_404()
    
    db.session.delete(notification)
    db.session.commit()
    
    return jsonify({'success': True})

@notifications_bp.route('/clear-read', methods=['POST'])
@login_required
def clear_read():
    """읽은 알림 모두 삭제"""
    notifications = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=True
    ).all()
    
    for notification in notifications:
        db.session.delete(notification)
    
    db.session.commit()
    
    return jsonify({'success': True, 'count': len(notifications)})

@notifications_bp.route('/api/unread-count')
@login_required
def api_unread_count():
    """읽지 않은 알림 개수 API"""
    count = Notification.get_unread_count(current_user.id)
    return jsonify({'count': count})