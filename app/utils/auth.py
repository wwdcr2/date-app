"""인증 관련 유틸리티 (레거시 호환성을 위해 유지)"""

from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

# 새로운 보안 모듈로 이동됨
from app.utils.security import couple_relationship_required

def couple_required(f):
    """커플 연결이 필요한 페이지에 사용하는 데코레이터 (레거시)"""
    return couple_relationship_required(f)