"""질문 관련 라우트"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, date
from sqlalchemy import func, and_
from app.extensions import db
from app.models.question import Question, DailyQuestion, Answer
from app.data.questions import CATEGORIES, DIFFICULTIES
from app.utils.security import (
    couple_relationship_required, 
    validate_couple_access, 
    sanitize_input,
    validate_form_data
)
import random

# 블루프린트 생성
questions_bp = Blueprint('questions', __name__, url_prefix='/questions')

@questions_bp.route('/')
@login_required
@couple_relationship_required
def index():
    """질문 메인 페이지"""
    # 커플 연결 확인
    connection = current_user.get_couple_connection()
    if not connection:
        flash('파트너와 연결된 후 질문 기능을 사용할 수 있습니다.', 'warning')
        return redirect(url_for('couple.connect'))
    
    return render_template('questions/index.html', 
                         categories=CATEGORIES,
                         difficulties=DIFFICULTIES)

@questions_bp.route('/daily')
@login_required
@couple_relationship_required
def daily():
    """오늘의 질문 페이지"""
    # 커플 연결 확인
    connection = current_user.get_couple_connection()
    if not connection:
        flash('파트너와 연결된 후 질문 기능을 사용할 수 있습니다.', 'warning')
        return redirect(url_for('couple.connect'))
    
    # 오늘의 일일 질문 가져오기 또는 생성
    daily_question = get_or_create_daily_question(connection.id)
    
    if not daily_question:
        flash('오늘의 질문을 불러올 수 없습니다.', 'error')
        return redirect(url_for('questions.index'))
    
    # 내 답변 확인
    my_answer = daily_question.get_user_answer(current_user.id)
    
    # 파트너 답변 확인 (내가 답변한 경우에만)
    partner_answer = daily_question.get_partner_answer(current_user.id)
    partner = current_user.get_partner()
    
    return render_template('questions/daily.html',
                         daily_question=daily_question,
                         question=daily_question.question,
                         my_answer=my_answer,
                         partner_answer=partner_answer,
                         partner=partner,
                         can_view_partner=my_answer is not None,
                         categories=CATEGORIES,
                         difficulties=DIFFICULTIES)

@questions_bp.route('/answer', methods=['POST'])
@login_required
@couple_relationship_required
def answer():
    """질문에 답변하기"""
    # 커플 연결 확인
    connection = current_user.get_couple_connection()
    if not connection:
        return jsonify({'success': False, 'message': '커플 연결이 필요합니다.'})
    
    try:
        # 입력 데이터 검증 및 정제
        data = request.get_json(force=True) or {}
        question_id = data.get('question_id')
        answer_text = sanitize_input(data.get('answer', '').strip(), max_length=2000)
        answer_date = data.get('date', date.today().isoformat())
        
        # 기본 검증
        if not question_id or not isinstance(question_id, int) or question_id <= 0:
            return jsonify({'success': False, 'message': '유효한 질문 ID를 입력해주세요.'})
        
        if not answer_text or len(answer_text.strip()) < 5:
            return jsonify({'success': False, 'message': '답변은 최소 5자 이상 입력해주세요.'})
        
        if len(answer_text) > 2000:
            return jsonify({'success': False, 'message': '답변은 최대 2000자까지 입력 가능합니다.'})
        
        # 날짜 파싱 및 검증
        try:
            answer_date = date.fromisoformat(answer_date) if isinstance(answer_date, str) else answer_date
            # 미래 날짜 방지
            if answer_date > date.today():
                answer_date = date.today()
        except ValueError:
            answer_date = date.today()
        
        # 질문 존재 확인
        question = Question.query.get(question_id)
        if not question:
            return jsonify({'success': False, 'message': '질문을 찾을 수 없습니다.'})
        
        # 이미 답변했는지 확인
        existing_answer = Answer.query.filter_by(
            question_id=question_id,
            user_id=current_user.id,
            date=answer_date
        ).first()
        
        if existing_answer:
            # 기존 답변 수정
            existing_answer.answer_text = answer_text
            existing_answer.updated_at = datetime.utcnow()
            is_update = True
        else:
            # 새 답변 생성
            new_answer = Answer(
                question_id=question_id,
                user_id=current_user.id,
                answer_text=answer_text,
                date=answer_date
            )
            db.session.add(new_answer)
            is_update = False
        
        db.session.commit()
        
        # 실시간 알림 전송 (새 답변인 경우에만)
        if not is_update:
            from app.socketio_events import notify_new_answer
            notify_new_answer(current_user.id, question.text)
        
        # 파트너 답변 조회 가능 여부 확인
        partner_answer = None
        if not is_update:  # 새 답변인 경우에만 파트너 답변 확인
            partner = current_user.get_partner()
            if partner:
                partner_answer = Answer.query.filter_by(
                    question_id=question_id,
                    user_id=partner.id,
                    date=answer_date
                ).first()
        
        return jsonify({
            'success': True, 
            'message': '답변이 저장되었습니다.' if not is_update else '답변이 수정되었습니다.',
            'is_update': is_update,
            'can_view_partner': True,
            'has_partner_answer': partner_answer is not None
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'답변 저장 중 오류가 발생했습니다: {str(e)}'})

@questions_bp.route('/history')
@login_required
@couple_relationship_required
def history():
    """질문 답변 히스토리"""
    # 커플 연결 확인
    connection = current_user.get_couple_connection()
    if not connection:
        flash('파트너와 연결된 후 질문 기능을 사용할 수 있습니다.', 'warning')
        return redirect(url_for('couple.connect'))
    
    # 페이지네이션 파라미터
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # 필터 파라미터 검증 및 정제
    category = sanitize_input(request.args.get('category', ''))
    start_date = sanitize_input(request.args.get('start_date', ''))
    end_date = sanitize_input(request.args.get('end_date', ''))
    
    # 카테고리 검증
    if category and category not in CATEGORIES:
        category = None
    
    # 내가 답변한 질문들 조회 (최신순)
    query = Answer.query.filter_by(user_id=current_user.id).join(Question)
    
    # 카테고리 필터
    if category and category in CATEGORIES:
        query = query.filter(Question.category == category)
    
    # 날짜 필터
    if start_date:
        try:
            start_date = date.fromisoformat(start_date)
            query = query.filter(Answer.date >= start_date)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date = date.fromisoformat(end_date)
            query = query.filter(Answer.date <= end_date)
        except ValueError:
            pass
    
    my_answers = query.order_by(Answer.date.desc(), Answer.created_at.desc())\
                     .paginate(page=page, per_page=per_page, error_out=False)
    
    # 각 답변에 대한 파트너 답변도 함께 조회 (접근 권한 확인 후)
    partner = current_user.get_partner()
    answer_pairs = []
    
    for my_answer in my_answers.items:
        # 내가 답변했으므로 파트너 답변 조회 가능
        partner_answer = None
        if partner:
            partner_answer = Answer.query.filter_by(
                question_id=my_answer.question_id,
                user_id=partner.id,
                date=my_answer.date
            ).first()
        
        answer_pairs.append({
            'question': my_answer.question,
            'my_answer': my_answer,
            'partner_answer': partner_answer,
            'date': my_answer.date,
            'both_answered': partner_answer is not None
        })
    
    return render_template('questions/history.html',
                         answer_pairs=answer_pairs,
                         pagination=my_answers,
                         partner=partner,
                         selected_category=category,
                         start_date=start_date,
                         end_date=end_date,
                         categories=CATEGORIES,
                         difficulties=DIFFICULTIES)

@questions_bp.route('/browse')
@login_required
@couple_relationship_required
def browse():
    """질문 둘러보기"""
    # 커플 연결 확인
    connection = current_user.get_couple_connection()
    if not connection:
        flash('파트너와 연결된 후 질문 기능을 사용할 수 있습니다.', 'warning')
        return redirect(url_for('couple.connect'))
    
    # 필터 파라미터 검증 및 정제
    category = sanitize_input(request.args.get('category', ''))
    difficulty = sanitize_input(request.args.get('difficulty', ''))
    page = max(1, request.args.get('page', 1, type=int))  # 최소값 1
    per_page = min(50, max(10, request.args.get('per_page', 20, type=int)))  # 10-50 범위
    
    # 카테고리 및 난이도 검증
    if category and category not in CATEGORIES:
        category = None
    if difficulty and difficulty not in DIFFICULTIES:
        difficulty = None
    
    # 질문 쿼리 구성
    query = Question.query
    
    if category and category in CATEGORIES:
        query = query.filter(Question.category == category)
    
    if difficulty and difficulty in DIFFICULTIES:
        query = query.filter(Question.difficulty == difficulty)
    
    # 페이지네이션
    questions = query.order_by(func.random()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('questions/browse.html',
                         questions=questions,
                         selected_category=category,
                         selected_difficulty=difficulty,
                         categories=CATEGORIES,
                         difficulties=DIFFICULTIES)

@questions_bp.route('/api/daily-question')
@login_required
@couple_relationship_required
def api_daily_question():
    """오늘의 질문 API"""
    # 커플 연결 확인
    connection = current_user.get_couple_connection()
    if not connection:
        return jsonify({'success': False, 'message': '커플 연결이 필요합니다.'})
    
    # 오늘의 일일 질문 가져오기
    daily_question = get_or_create_daily_question(connection.id)
    
    if not daily_question:
        return jsonify({'success': False, 'message': '오늘의 질문을 찾을 수 없습니다.'})
    
    # 답변 상태 확인
    my_answer = daily_question.get_user_answer(current_user.id)
    partner_answer = daily_question.get_partner_answer(current_user.id)
    partner = current_user.get_partner()
    
    return jsonify({
        'success': True,
        'question': {
            'id': daily_question.question.id,
            'text': daily_question.question.text,
            'category': daily_question.question.category,
            'difficulty': daily_question.question.difficulty,
            'category_info': CATEGORIES.get(daily_question.question.category, {}),
            'difficulty_info': DIFFICULTIES.get(daily_question.question.difficulty, {})
        },
        'my_answer': {
            'text': my_answer.answer_text,
            'created_at': my_answer.created_at.isoformat(),
            'updated_at': my_answer.updated_at.isoformat() if my_answer.updated_at else None
        } if my_answer else None,
        'partner_answer': {
            'text': partner_answer.answer_text,
            'created_at': partner_answer.created_at.isoformat(),
            'updated_at': partner_answer.updated_at.isoformat() if partner_answer.updated_at else None
        } if partner_answer else None,
        'can_see_partner_answer': my_answer is not None,
        'partner_name': partner.name if partner else None,
        'answer_status': daily_question.get_answer_status()
    })

@questions_bp.route('/api/answer-status/<int:question_id>')
@login_required
@couple_relationship_required
def api_answer_status(question_id):
    """특정 질문의 답변 상태 확인 API"""
    # 커플 연결 확인
    connection = current_user.get_couple_connection()
    if not connection:
        return jsonify({'success': False, 'message': '커플 연결이 필요합니다.'})
    
    # 날짜 파라미터 (기본값: 오늘)
    check_date = request.args.get('date', date.today().isoformat())
    try:
        check_date = date.fromisoformat(check_date)
    except ValueError:
        check_date = date.today()
    
    # 질문 존재 확인
    question = Question.query.get(question_id)
    if not question:
        return jsonify({'success': False, 'message': '질문을 찾을 수 없습니다.'})
    
    # 답변 상태 확인
    partner = current_user.get_partner()
    if not partner:
        return jsonify({'success': False, 'message': '파트너 정보를 찾을 수 없습니다.'})
    
    status = Answer.get_answer_completion_status(
        question_id, check_date, current_user.id, partner.id
    )
    
    # 접근 권한 확인
    can_view_partner = status['user1_answered'] if current_user.id == connection.user1_id else status['user2_answered']
    
    return jsonify({
        'success': True,
        'question_id': question_id,
        'date': check_date.isoformat(),
        'my_answered': status['user1_answered'] if current_user.id == connection.user1_id else status['user2_answered'],
        'partner_answered': status['user2_answered'] if current_user.id == connection.user1_id else status['user1_answered'],
        'both_answered': status['both_answered'],
        'can_view_partner_answer': can_view_partner,
        'my_answer': {
            'text': status['user1_answer'].answer_text if status['user1_answer'] and current_user.id == connection.user1_id else 
                   (status['user2_answer'].answer_text if status['user2_answer'] and current_user.id == connection.user2_id else None),
            'created_at': (status['user1_answer'].created_at.isoformat() if status['user1_answer'] and current_user.id == connection.user1_id else 
                          (status['user2_answer'].created_at.isoformat() if status['user2_answer'] and current_user.id == connection.user2_id else None))
        } if (status['user1_answer'] and current_user.id == connection.user1_id) or (status['user2_answer'] and current_user.id == connection.user2_id) else None,
        'partner_answer': {
            'text': status['user2_answer'].answer_text if status['user2_answer'] and current_user.id == connection.user1_id and can_view_partner else 
                   (status['user1_answer'].answer_text if status['user1_answer'] and current_user.id == connection.user2_id and can_view_partner else None),
            'created_at': (status['user2_answer'].created_at.isoformat() if status['user2_answer'] and current_user.id == connection.user1_id and can_view_partner else 
                          (status['user1_answer'].created_at.isoformat() if status['user1_answer'] and current_user.id == connection.user2_id and can_view_partner else None))
        } if can_view_partner and ((status['user2_answer'] and current_user.id == connection.user1_id) or (status['user1_answer'] and current_user.id == connection.user2_id)) else None
    })

@questions_bp.route('/api/history-stats')
@login_required
@couple_relationship_required
def api_history_stats():
    """답변 히스토리 통계 API"""
    # 커플 연결 확인
    connection = current_user.get_couple_connection()
    if not connection:
        return jsonify({'success': False, 'message': '커플 연결이 필요합니다.'})
    
    partner = current_user.get_partner()
    if not partner:
        return jsonify({'success': False, 'message': '파트너 정보를 찾을 수 없습니다.'})
    
    # 통계 계산
    from sqlalchemy import func
    
    # 내가 답변한 총 질문 수
    my_total_answers = Answer.query.filter_by(user_id=current_user.id).count()
    
    # 파트너가 답변한 총 질문 수
    partner_total_answers = Answer.query.filter_by(user_id=partner.id).count()
    
    # 둘 다 답변한 질문 수 (같은 날짜, 같은 질문)
    both_answered = db.session.query(Answer.question_id, Answer.date).filter_by(user_id=current_user.id)\
                             .intersect(
                                 db.session.query(Answer.question_id, Answer.date).filter_by(user_id=partner.id)
                             ).count()
    
    # 카테고리별 답변 통계
    category_stats = db.session.query(
        Question.category,
        func.count(Answer.id).label('count')
    ).join(Answer).filter(Answer.user_id == current_user.id)\
     .group_by(Question.category).all()
    
    # 최근 7일간 답변 통계
    from datetime import timedelta
    week_ago = date.today() - timedelta(days=7)
    recent_answers = Answer.query.filter(
        Answer.user_id == current_user.id,
        Answer.date >= week_ago
    ).count()
    
    return jsonify({
        'success': True,
        'stats': {
            'my_total_answers': my_total_answers,
            'partner_total_answers': partner_total_answers,
            'both_answered': both_answered,
            'recent_answers': recent_answers,
            'category_stats': [
                {
                    'category': cat_stat.category,
                    'count': cat_stat.count,
                    'name': CATEGORIES.get(cat_stat.category, {}).get('name', cat_stat.category),
                    'emoji': CATEGORIES.get(cat_stat.category, {}).get('emoji', '📝')
                }
                for cat_stat in category_stats
            ]
        }
    })

def get_or_create_daily_question(couple_id):
    """커플을 위한 오늘의 일일 질문 가져오기 또는 생성"""
    today = date.today()
    
    # 오늘의 일일 질문이 이미 있는지 확인
    daily_question = DailyQuestion.query.filter_by(
        couple_id=couple_id,
        date=today
    ).first()
    
    if daily_question:
        return daily_question
    
    # 새로운 일일 질문 생성
    # 시드를 커플 ID와 오늘 날짜로 설정하여 같은 커플은 같은 질문을 받도록 함
    seed = f"{couple_id}-{today.isoformat()}"
    random.seed(seed)
    
    # 사용 가능한 질문들 중에서 선택
    available_questions = Question.query.all()
    
    if not available_questions:
        return None
    
    # 랜덤하게 질문 선택 (시드가 설정되어 있어 같은 커플은 같은 질문)
    selected_question = random.choice(available_questions)
    
    # 새 일일 질문 생성
    daily_question = DailyQuestion(
        couple_id=couple_id,
        question_id=selected_question.id,
        date=today
    )
    
    try:
        db.session.add(daily_question)
        db.session.commit()
        return daily_question
    except Exception as e:
        db.session.rollback()
        # 동시성 문제로 이미 생성된 경우 다시 조회
        return DailyQuestion.query.filter_by(
            couple_id=couple_id,
            date=today
        ).first()