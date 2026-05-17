# CANJIA - 제주 산업 발전 및 네트워크 공동체

Community for Association & Network in Jeju Industry Association

## 개요

CANJIA는 제주도에서의 산업 발전과 네트워크 구축을 목표로 하는 공동체 웹 플랫폼입니다. 인공지능(AGI), 안드로이드 사이보그 트랜스포머(ACTF) 개발부터 스포츠 활동, 카페 창업까지 다양한 분야에서 회원들이 협력하고 성장할 수 있는 플랫폼을 제공합니다.

## 작성 정보

- **작성인**: 정구영
- **작성일**: 2026년 05월 15일
- **약자**: CANJIA

## 주요 기능

### 1. 인증 시스템
- Microsoft OAuth 2.0을 통한 로그인
- 사용자 프로필 관리
- 세션 관리

### 2. 분야별 커뮤니티
- **AGI (범용 인공 지능)**: 사람의 수준에 맞고 사람의 활동 및 외관을 본따서 만든 인공지능
- **ACTF (안드로이드 사이보그 트랜스포머)**: 영화 트랜스포머를 1번 기준에 따라 구현
- **수영**: 무중력 환경을 간접 체험하게 해주는 환경
- **스카이 다이빙**: 하늘에서의 중력을 활용해서 활강하는 스포츠
- **암벽 등반**: 중력을 거슬러서 해당 구조물을 오르는 스포츠 활동
- **카페 취업**: 제주도에 있는 관심이 있는 카페 방문 및 경제 활동 여건 탐색
- **기술 연마**: 카페 창업 도전을 위한 바리스타 기술 확보

### 3. 문서 관리
- 분야별 문서 작성 및 공유
- 구글 문서와 유사한 편집 환경
- 공개/비공개 문서 설정
- 문서 수정 및 삭제

### 4. 사용자 기능
- 프로필 관리
- 분야 가입/탈퇴
- 내 문서 관리
- 대시보드

## 목표

1. **경제 자립**: 배우고 학습할 때는 지났다. 이젠 사람들과 뭔가를 해야 한다.
2. **취미 생활**: 취미 생활이 경제 자립 수단이고, 그 중 아르바이트로라도 벌어야 한다.
3. **기술 증진**: 인생의 본 목표로 기술의 도약 실행을 주거 이전 이후에 시작할 것이다.
4. **회원 모집**: 혼자서 할 수 없는 일이긴 하지만, 나의 노력의 결실은 반듯이 죽어도 이룬다.
5. **주거 이전**: 제주도 외에는 해당 항목들을 모두 이행할 수 있는 곳은 아예 존재하지 않아.
6. **생명 연장**: 생명 연장을 기술적으로 완성해서 도약의 시초를 완성할 초석을 마련한다.
7. **우주 유영**: 도약의 정점이 바로 이 부분이고, AGI & ACTF 의 영역이 바로 이것이다.

## 설치 방법

### 1. 필수 요구사항
- Python 3.8 이상
- pip (Python 패키지 관리자)
- Microsoft Azure 계정 (OAuth용)

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
SECRET_KEY=your-secret-key-here
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
MICROSOFT_TENANT_ID=common
DATABASE_URL=sqlite:///canjia.db
```

### 4. Microsoft OAuth 설정

1. [Microsoft Azure Portal](https://portal.azure.com/)에 접속
2. Azure Active Directory > 앱 등록
3. 새 앱 등록
4. 리디렉션 URI에 `http://localhost:5000/auth/callback` 추가
5. 클라이언트 ID 및 클라이언트 시크릿 복사
6. `.env` 파일에 붙여넣기

### 5. 애플리케이션 실행

```bash
python app.py
```

애플리케이션이 `http://localhost:5000`에서 실행됩니다.

## 프로젝트 구조

```
CANJIA0518/
├── app.py                 # 메인 Flask 애플리케이션
├── config.py              # 설정 파일
├── models.py              # 데이터베이스 모델
├── requirements.txt       # Python 의존성
├── .env.example          # 환경 변수 예시
├── README.md             # 프로젝트 문서
├── templates/            # HTML 템플릿
│   ├── base.html         # 기본 템플릿
│   ├── index.html        # 메인 페이지
│   ├── dashboard.html    # 대시보드
│   ├── profile.html      # 프로필 페이지
│   ├── edit_profile.html # 프로필 수정
│   ├── field_detail.html # 분야 상세
│   ├── document_detail.html  # 문서 상세
│   ├── edit_document.html    # 문서 편집
│   └── my_documents.html      # 내 문서
└── static/               # 정적 파일
    ├── css/
    │   └── style.css    # 사용자 정의 스타일
    └── js/
        └── main.js      # JavaScript 기능
```

## 기술 스택

- **백엔드**: Flask (Python)
- **데이터베이스**: SQLite (SQLAlchemy)
- **인증**: Microsoft OAuth 2.0 (Authlib)
- **프론트엔드**: HTML5, Bootstrap 5, JavaScript
- **세션 관리**: Flask-Login

## 데이터베이스 모델

### User
- 사용자 정보
- Microsoft 계정 연동
- 프로필 관리

### Field
- 분야 정보
- 분야별 문서 관리

### Document
- 문서 정보
- 공개/비공개 설정
- 작성자 및 분야 연관

### FieldMembership
- 사용자-분야 관계
- 가입/탈퇴 관리

## 개발 환경

- **개발환경**: Google Colab - Gemini
- **웹 페이지 구현환경**: Flask
- **로그인 환경**: Microsoft Client - ID & Secret

## 라이선스

이 프로젝트는 CANJIA 커뮤니티의 소유입니다.

## 연락처

질문이나 제안이 있으시면 프로젝트 관리자에게 문의해주세요.

---

**CANJIA - Community for Association & Network in Jeju Industry Association**
