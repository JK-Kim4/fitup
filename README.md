# 핏업 (Fitup)

> 지원서의 '핏'을 올리는 가장 빠른 방법

AI 기반 이력서-채용공고 적합도 분석 서비스입니다. 채용공고(JD)와 이력서를 업로드하면 AI가 적합도를 분석하고 점수, 강점, 리스크, 개선점을 제공합니다.

## 주요 기능

- **적합도 점수 산출**: 자격요건, 우대사항, 기술스택, 컬쳐핏 등 카테고리별 점수 (0~100점)
- **매칭 분석**: JD 항목별 이력서 근거 매칭 및 판정
- **강점/리스크 도출**: 지원자의 핵심 강점과 보완이 필요한 영역 분석
- **개선 가이드**: 이력서 수정 방향 및 면접 대비 질문 제공
- **파일 업로드 지원**: PDF, Markdown, TXT 형식 지원
- **AI 모델 선택**: OpenAI GPT-4o / Anthropic Claude 선택 가능
- **카카오 로그인**: OAuth 2.0 소셜 로그인 지원
- **요청 제한**: 비로그인 하루 1회 / 로그인 하루 3회

## 기술 스택

- **Backend**: Django 5.x, Gunicorn
- **AI**: OpenAI API, Anthropic API
- **PDF 파싱**: PyMuPDF
- **Database**: PostgreSQL 16 (Docker)
- **인증**: 카카오 OAuth 2.0
- **Frontend**: Bootstrap 5, Marked.js

## 설치 및 실행

### 사전 요구사항

- Python 3.11+
- Docker Desktop

### 1. 저장소 클론

```bash
git clone <repository-url>
cd resume-evaluation
```

### 2. 가상환경 생성

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 환경변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 열어 실제 값을 입력합니다:

```
DB_NAME=resume_eval
DB_USER=resume_user
DB_PASSWORD=your-db-password

DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True

OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

KAKAO_CLIENT_ID=your-kakao-client-id
KAKAO_CLIENT_SECRET=your-kakao-client-secret
```

### 4. 배포 스크립트 실행

```bash
./deploy.sh
```

서버 실행 후 http://localhost:8000 접속

> `deploy.sh`는 PostgreSQL 컨테이너 기동 → 패키지 설치 → 마이그레이션 → 정적 파일 수집 → Gunicorn 시작을 자동으로 처리합니다.

### 서버 종료

```bash
./stop.sh
```

---

### 개발 환경에서 직접 실행하는 경우

```bash
# 1. PostgreSQL 컨테이너만 시작
docker compose up -d

# 2. 패키지 설치
pip install -r requirements.txt

# 3. 마이그레이션
python manage.py migrate

# 4. 개발 서버 실행
python manage.py runserver
```

## 프로젝트 구조

```
resume-evaluation/
├── config/                 # Django 프로젝트 설정
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── evaluator/              # 메인 애플리케이션
│   ├── migrations/         # DB 마이그레이션
│   ├── social_auth/        # 소셜 로그인 provider 모듈
│   ├── templates/          # HTML 템플릿
│   ├── admin.py            # 어드민 등록
│   ├── auth_views.py       # OAuth 로그인/콜백/로그아웃 뷰
│   ├── forms.py            # 입력 폼
│   ├── models.py           # DB 모델 (RequestLog, SocialProfile, AnalysisHistory)
│   ├── file_parser.py      # 파일 파싱 (PDF/MD/TXT)
│   ├── views.py            # 분석 뷰 로직
│   └── urls.py             # URL 라우팅
├── prompt/
│   └── prompt.md           # AI 시스템 프롬프트
├── llm_client.py           # LLM API 클라이언트
├── docker-compose.yml      # PostgreSQL 컨테이너 정의
├── deploy.sh               # 배포 자동화 스크립트
├── stop.sh                 # 서버 종료 스크립트
├── .env.example            # 환경변수 템플릿
├── manage.py
└── requirements.txt
```

## 환경변수

| 변수명 | 필수 | 설명 | 기본값 |
|--------|------|------|--------|
| `DB_NAME` | ✓ | PostgreSQL DB 이름 | `resume_eval` |
| `DB_USER` | ✓ | PostgreSQL 사용자 | `resume_user` |
| `DB_PASSWORD` | ✓ | PostgreSQL 비밀번호 | - |
| `DB_HOST` | ✕ | DB 호스트 | `localhost` |
| `DB_PORT` | ✕ | DB 포트 | `5432` |
| `OPENAI_API_KEY` | △ | OpenAI API 키 | - |
| `ANTHROPIC_API_KEY` | △ | Anthropic API 키 | - |
| `DJANGO_SECRET_KEY` | ✕ | Django 시크릿 키 | 개발용 키 |
| `DJANGO_DEBUG` | ✕ | 디버그 모드 | `True` |
| `KAKAO_CLIENT_ID` | ✕ | 카카오 OAuth Client ID | - |
| `KAKAO_CLIENT_SECRET` | ✕ | 카카오 OAuth Client Secret | - |

> △: AI 기능 사용 시 둘 중 하나 이상 필요

## 요청 제한

| 구분 | 일일 한도 | 초기화 기준 |
|------|----------|------------|
| 비로그인 (IP 기반) | 1회 | 자정 (Asia/Seoul) |
| 카카오 로그인 | 3회 | 자정 (Asia/Seoul) |

분석 성공 시에만 카운트 차감됩니다.

## 라이선스

MIT License
