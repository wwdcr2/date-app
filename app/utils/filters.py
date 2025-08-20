"""Jinja2 커스텀 필터"""

import re
from markupsafe import Markup

def highlight_search(text, query):
    """검색어를 하이라이트 처리"""
    if not query or not text:
        return text
    
    # 특수 문자 이스케이프
    escaped_query = re.escape(query)
    
    # 대소문자 구분 없이 검색어 하이라이트
    pattern = re.compile(f'({escaped_query})', re.IGNORECASE)
    highlighted = pattern.sub(r'<span class="highlight">\1</span>', str(text))
    
    return Markup(highlighted)

def nl2br(text):
    """줄바꿈을 <br> 태그로 변환"""
    if not text:
        return ''
    
    # 줄바꿈을 <br> 태그로 변환
    return Markup(str(text).replace('\n', '<br>'))

def strftime_filter(datetime_obj, format_string='%Y-%m-%d'):
    """날짜/시간 포맷팅 필터"""
    if not datetime_obj:
        return ''
    
    try:
        return datetime_obj.strftime(format_string)
    except (AttributeError, ValueError):
        return str(datetime_obj)

def register_filters(app):
    """Flask 앱에 커스텀 필터 등록"""
    app.jinja_env.filters['highlight_search'] = highlight_search
    app.jinja_env.filters['nl2br'] = nl2br
    app.jinja_env.filters['strftime'] = strftime_filter