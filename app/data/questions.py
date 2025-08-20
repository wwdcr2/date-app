"""질문 데이터"""

# 카테고리별 질문 데이터
QUESTIONS_DATA = [
    # 일상 & 취미 (category: daily)
    {
        'category': 'daily',
        'difficulty': 'easy',
        'text': '오늘 하루 중 가장 기뻤던 순간은 언제였나요?'
    },
    {
        'category': 'daily',
        'difficulty': 'easy',
        'text': '요즘 가장 관심 있는 취미나 활동이 있나요?'
    },
    {
        'category': 'daily',
        'difficulty': 'easy',
        'text': '스트레스를 받을 때 어떻게 해소하시나요?'
    },
    {
        'category': 'daily',
        'difficulty': 'easy',
        'text': '좋아하는 음식과 그 이유를 알려주세요.'
    },
    {
        'category': 'daily',
        'difficulty': 'easy',
        'text': '주말에 가장 하고 싶은 일은 무엇인가요?'
    },
    {
        'category': 'daily',
        'difficulty': 'medium',
        'text': '어린 시절 가장 좋아했던 놀이나 게임은 무엇이었나요?'
    },
    {
        'category': 'daily',
        'difficulty': 'medium',
        'text': '만약 하루 종일 자유시간이 있다면 무엇을 하고 싶나요?'
    },
    {
        'category': 'daily',
        'difficulty': 'medium',
        'text': '새로운 취미를 시작한다면 무엇을 해보고 싶나요?'
    },
    
    # 관계 & 사랑 (category: relationship)
    {
        'category': 'relationship',
        'difficulty': 'easy',
        'text': '상대방의 어떤 점이 가장 매력적이라고 생각하나요?'
    },
    {
        'category': 'relationship',
        'difficulty': 'easy',
        'text': '함께 있을 때 가장 행복한 순간은 언제인가요?'
    },
    {
        'category': 'relationship',
        'difficulty': 'easy',
        'text': '상대방에게 고마운 점이 있다면 무엇인가요?'
    },
    {
        'category': 'relationship',
        'difficulty': 'medium',
        'text': '연인 관계에서 가장 중요하다고 생각하는 것은 무엇인가요?'
    },
    {
        'category': 'relationship',
        'difficulty': 'medium',
        'text': '갈등이 생겼을 때 어떻게 해결하는 것이 좋다고 생각하나요?'
    },
    {
        'category': 'relationship',
        'difficulty': 'medium',
        'text': '상대방과 함께 만들고 싶은 추억이 있나요?'
    },
    {
        'category': 'relationship',
        'difficulty': 'hard',
        'text': '서로에게 더 솔직해지려면 어떤 노력이 필요할까요?'
    },
    {
        'category': 'relationship',
        'difficulty': 'hard',
        'text': '우리 관계에서 더 발전시키고 싶은 부분이 있나요?'
    },
    
    # 꿈 & 목표 (category: dreams)
    {
        'category': 'dreams',
        'difficulty': 'easy',
        'text': '올해 꼭 이루고 싶은 목표가 있나요?'
    },
    {
        'category': 'dreams',
        'difficulty': 'easy',
        'text': '어릴 때 꿈꿨던 직업이 있나요?'
    },
    {
        'category': 'dreams',
        'difficulty': 'medium',
        'text': '5년 후의 자신은 어떤 모습일 것 같나요?'
    },
    {
        'category': 'dreams',
        'difficulty': 'medium',
        'text': '가장 가보고 싶은 여행지와 그 이유는 무엇인가요?'
    },
    {
        'category': 'dreams',
        'difficulty': 'medium',
        'text': '새로운 도전을 한다면 무엇을 해보고 싶나요?'
    },
    {
        'category': 'dreams',
        'difficulty': 'hard',
        'text': '인생에서 가장 중요하게 생각하는 가치는 무엇인가요?'
    },
    {
        'category': 'dreams',
        'difficulty': 'hard',
        'text': '10년 후 우리는 어떤 모습으로 함께하고 있을까요?'
    },
    
    # 추억 & 경험 (category: memories)
    {
        'category': 'memories',
        'difficulty': 'easy',
        'text': '가장 기억에 남는 생일은 언제였나요?'
    },
    {
        'category': 'memories',
        'difficulty': 'easy',
        'text': '어린 시절 가장 좋아했던 장소는 어디였나요?'
    },
    {
        'category': 'memories',
        'difficulty': 'medium',
        'text': '지금까지 받은 선물 중 가장 기억에 남는 것은?'
    },
    {
        'category': 'memories',
        'difficulty': 'medium',
        'text': '처음 만났을 때의 첫인상을 솔직히 말해주세요.'
    },
    {
        'category': 'memories',
        'difficulty': 'medium',
        'text': '함께한 데이트 중 가장 기억에 남는 순간은?'
    },
    {
        'category': 'memories',
        'difficulty': 'hard',
        'text': '인생에서 가장 힘들었던 시기를 어떻게 극복했나요?'
    },
    {
        'category': 'memories',
        'difficulty': 'hard',
        'text': '지금까지 살면서 가장 후회되는 일이 있나요?'
    },
    
    # 재미있는 질문 (category: fun)
    {
        'category': 'fun',
        'difficulty': 'easy',
        'text': '동물로 태어난다면 무엇이 되고 싶나요?'
    },
    {
        'category': 'fun',
        'difficulty': 'easy',
        'text': '초능력을 하나 가질 수 있다면 무엇을 선택하겠나요?'
    },
    {
        'category': 'fun',
        'difficulty': 'easy',
        'text': '무인도에 하나만 가져갈 수 있다면 무엇을 선택하겠나요?'
    },
    {
        'category': 'fun',
        'difficulty': 'medium',
        'text': '시간여행이 가능하다면 언제로 가고 싶나요?'
    },
    {
        'category': 'fun',
        'difficulty': 'medium',
        'text': '하루 동안 다른 사람이 될 수 있다면 누가 되고 싶나요?'
    },
    {
        'category': 'fun',
        'difficulty': 'medium',
        'text': '로또에 당첨된다면 가장 먼저 무엇을 하겠나요?'
    },
    {
        'category': 'fun',
        'difficulty': 'hard',
        'text': '만약 세상에서 하나의 문제를 해결할 수 있다면 무엇을 선택하겠나요?'
    },
    
    # 깊은 대화 (category: deep)
    {
        'category': 'deep',
        'difficulty': 'medium',
        'text': '행복이란 무엇이라고 생각하나요?'
    },
    {
        'category': 'deep',
        'difficulty': 'medium',
        'text': '가족에게 가장 고마운 점은 무엇인가요?'
    },
    {
        'category': 'deep',
        'difficulty': 'hard',
        'text': '인생에서 가장 중요한 것은 무엇이라고 생각하나요?'
    },
    {
        'category': 'deep',
        'difficulty': 'hard',
        'text': '죽기 전에 꼭 해보고 싶은 일이 있나요?'
    },
    {
        'category': 'deep',
        'difficulty': 'hard',
        'text': '만약 내일이 마지막 날이라면 무엇을 하고 싶나요?'
    },
    {
        'category': 'deep',
        'difficulty': 'hard',
        'text': '지금의 나에게 가장 필요한 것은 무엇일까요?'
    }
]

# 카테고리 정보
CATEGORIES = {
    'daily': {
        'name': '일상 & 취미',
        'description': '일상생활과 취미에 관한 가벼운 질문들',
        'emoji': '☀️'
    },
    'relationship': {
        'name': '관계 & 사랑',
        'description': '서로의 관계와 사랑에 대한 질문들',
        'emoji': '💕'
    },
    'dreams': {
        'name': '꿈 & 목표',
        'description': '미래의 꿈과 목표에 관한 질문들',
        'emoji': '🌟'
    },
    'memories': {
        'name': '추억 & 경험',
        'description': '과거의 추억과 경험에 관한 질문들',
        'emoji': '📸'
    },
    'fun': {
        'name': '재미있는 질문',
        'description': '상상력을 자극하는 재미있는 질문들',
        'emoji': '🎭'
    },
    'deep': {
        'name': '깊은 대화',
        'description': '인생과 철학에 대한 깊이 있는 질문들',
        'emoji': '🤔'
    }
}

# 난이도 정보
DIFFICULTIES = {
    'easy': {
        'name': '쉬움',
        'description': '가벼운 마음으로 답할 수 있는 질문',
        'color': '#28A745'
    },
    'medium': {
        'name': '보통',
        'description': '조금 생각해볼 필요가 있는 질문',
        'color': '#FFC107'
    },
    'hard': {
        'name': '어려움',
        'description': '깊이 있는 성찰이 필요한 질문',
        'color': '#DC3545'
    }
}