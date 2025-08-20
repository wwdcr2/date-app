"""커플 연결 관련 라우트"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.models.user import User
from app.models.couple import CoupleConnection
from app.models.notification import Notification
from app.extensions import db
import string
import secrets

# 블루프린트 생성
couple_bp = Blueprint('couple', __name__)

@couple_bp.route('/connect')
@login_required
def connect():
    """커플 연결 페이지"""
    # 이미 연결된 경우 대시보드로 리다이렉트
    if current_user.is_connected_to_partner():
        flash('이미 파트너와 연결되어 있습니다.', 'info')
        return redirect(url_for('main.dashboard'))
    
    return render_template('couple/connect.html')

@couple_bp.route('/generate-invite', methods=['POST'])
@login_required
def generate_invite():
    """초대 코드 생성"""
    if current_user.is_connected_to_partner():
        return jsonify({
            'success': False, 
            'error': '이미 파트너와 연결되어 있습니다.'
        }), 400
    
    try:
        # 기존 연결 요청이 있는지 확인 (사용자가 생성한 것)
        existing_connection = CoupleConnection.query.filter_by(
            user1_id=current_user.id,
            user2_id=None  # 아직 연결되지 않은 상태
        ).first()
        
        if existing_connection:
            # 기존 초대 코드 반환
            invite_code = existing_connection.invite_code
        else:
            # 새 초대 코드 생성
            invite_code = CoupleConnection.generate_invite_code()
            
            # 새 연결 생성 (user2_id는 나중에 설정)
            connection = CoupleConnection(
                user1_id=current_user.id,
                user2_id=None,
                invite_code=invite_code
            )
            
            db.session.add(connection)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'invite_code': invite_code,
            'message': '초대 코드가 생성되었습니다.'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': '초대 코드 생성 중 오류가 발생했습니다.'
        }), 500

@couple_bp.route('/join-with-code', methods=['POST'])
@login_required
def join_with_code():
    """초대 코드로 연결"""
    if current_user.is_connected_to_partner():
        return jsonify({
            'success': False,
            'error': '이미 파트너와 연결되어 있습니다.'
        }), 400
    
    try:
        data = request.get_json(force=True) or {}
    except:
        data = request.form
    invite_code = data.get('invite_code', '').strip().upper()
    
    if not invite_code:
        return jsonify({
            'success': False,
            'error': '초대 코드를 입력해주세요.'
        }), 400
    
    if len(invite_code) != 6:
        return jsonify({
            'success': False,
            'error': '올바른 초대 코드를 입력해주세요. (6자리)'
        }), 400
    
    try:
        # 초대 코드로 연결 찾기
        connection = CoupleConnection.query.filter_by(
            invite_code=invite_code,
            user2_id=None  # 아직 연결되지 않은 상태
        ).first()
        
        if not connection:
            return jsonify({
                'success': False,
                'error': '유효하지 않은 초대 코드입니다.'
            }), 404
        
        # 자기 자신의 초대 코드인지 확인
        if connection.user1_id == current_user.id:
            return jsonify({
                'success': False,
                'error': '자신의 초대 코드로는 연결할 수 없습니다.'
            }), 400
        
        # 연결 완료
        connection.user2_id = current_user.id
        db.session.commit()
        
        # 파트너 정보 가져오기
        partner = User.query.get(connection.user1_id)
        
        # 양쪽 사용자에게 알림 생성
        Notification.create_notification(
            user_id=partner.id,
            notification_type='partner_connected',
            title='파트너 연결 완료',
            content=f'{current_user.name}님과 연결되었습니다!'
        )
        
        Notification.create_notification(
            user_id=current_user.id,
            notification_type='partner_connected',
            title='파트너 연결 완료',
            content=f'{partner.name}님과 연결되었습니다!'
        )
        
        return jsonify({
            'success': True,
            'message': f'{partner.name}님과 성공적으로 연결되었습니다!',
            'partner': {
                'id': partner.id,
                'name': partner.name,
                'email': partner.email
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': '연결 중 오류가 발생했습니다.'
        }), 500

@couple_bp.route('/disconnect', methods=['POST'])
@login_required
def disconnect():
    """파트너 연결 해제"""
    if not current_user.is_connected_to_partner():
        return jsonify({
            'success': False,
            'error': '연결된 파트너가 없습니다.'
        }), 400
    
    try:
        connection = current_user.get_couple_connection()
        partner = current_user.get_partner()
        
        if connection and partner:
            # 파트너에게 알림
            Notification.create_notification(
                user_id=partner.id,
                notification_type='partner_disconnected',
                title='파트너 연결 해제',
                content=f'{current_user.name}님이 연결을 해제했습니다.'
            )
            
            # 연결 삭제
            db.session.delete(connection)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': '파트너 연결이 해제되었습니다.'
            })
        else:
            return jsonify({
                'success': False,
                'error': '연결 정보를 찾을 수 없습니다.'
            }), 404
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': '연결 해제 중 오류가 발생했습니다.'
        }), 500

@couple_bp.route('/api/connection-status')
@login_required
def connection_status():
    """연결 상태 확인 API"""
    is_connected = current_user.is_connected_to_partner()
    partner = current_user.get_partner()
    
    data = {
        'is_connected': is_connected,
        'partner': None
    }
    
    if is_connected and partner:
        data['partner'] = {
            'id': partner.id,
            'name': partner.name,
            'email': partner.email,
            'created_at': partner.created_at.isoformat()
        }
    
    return jsonify(data)

@couple_bp.route('/api/pending-invites')
@login_required
def pending_invites():
    """대기 중인 초대 코드 확인"""
    pending_connection = CoupleConnection.query.filter_by(
        user1_id=current_user.id,
        user2_id=None
    ).first()
    
    if pending_connection:
        return jsonify({
            'has_pending': True,
            'invite_code': pending_connection.invite_code,
            'created_at': pending_connection.connected_at.isoformat()
        })
    else:
        return jsonify({
            'has_pending': False
        })

@couple_bp.route('/cancel-invite', methods=['POST'])
@login_required
def cancel_invite():
    """초대 코드 취소"""
    try:
        pending_connection = CoupleConnection.query.filter_by(
            user1_id=current_user.id,
            user2_id=None
        ).first()
        
        if pending_connection:
            db.session.delete(pending_connection)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': '초대 코드가 취소되었습니다.'
            })
        else:
            return jsonify({
                'success': False,
                'error': '취소할 초대 코드가 없습니다.'
            }), 404
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': '초대 코드 취소 중 오류가 발생했습니다.'
        }), 500