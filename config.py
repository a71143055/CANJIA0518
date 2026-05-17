import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Microsoft OAuth Configuration
    MICROSOFT_CLIENT_ID = os.environ.get('MICROSOFT_CLIENT_ID')
    MICROSOFT_CLIENT_SECRET = os.environ.get('MICROSOFT_CLIENT_SECRET')
    MICROSOFT_TENANT_ID = os.environ.get('MICROSOFT_TENANT_ID', 'common')
    
    # Microsoft OAuth Endpoints
    MICROSOFT_AUTH_URL = f'https://login.microsoftonline.com/{MICROSOFT_TENANT_ID}/oauth2/v2.0/authorize'
    MICROSOFT_TOKEN_URL = f'https://login.microsoftonline.com/{MICROSOFT_TENANT_ID}/oauth2/v2.0/token'
    MICROSOFT_GRAPH_API = 'https://graph.microsoft.com/v1.0/me'
    
    # Redirect URI
    REDIRECT_URI = 'http://localhost:5000/auth/callback'
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///canjia.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Fields Configuration
    FIELDS = [
        {'id': 'agi', 'name': 'AGI', 'description': '범용 인공 지능 - 사람의 수준에 맞고 사람의 활동 및 외관을 본따서 만든 인공지능'},
        {'id': 'actf', 'name': 'ACTF', 'description': '안드로이드 사이보그 트랜스포머 - 영화 트랜스포머를 1번 기준에 따라 구현'},
        {'id': 'swimming', 'name': '수영', 'description': '수영장은 무중력 환경을 간접 체험하게 해주는 환경'},
        {'id': 'skydiving', 'name': '스카이 다이빙', 'description': '하늘에서의 중력을 활용해서 활강하는 스포츠로, 중력에 적응할 수 있다'},
        {'id': 'climbing', 'name': '암벽 등반', 'description': '암벽등반은 중력을 거슬러서 해당 구조물을 오르는 스포츠 활동'},
        {'id': 'cafe', 'name': '카페 취업', 'description': '제주도에 있는 관심이 있는 카페 방문 및 경제 활동 여건을 탐색'},
        {'id': 'skills', 'name': '기술 연마', 'description': '카페 창업 도전을 위한 바리스타 기술 확보'}
    ]
    
    # Goals
    GOALS = [
        '경제 자립',
        '취미 생활',
        '기술 증진',
        '회원 모집',
        '주거 이전',
        '생명 연장',
        '우주 유영'
    ]
