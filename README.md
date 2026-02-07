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
- **IP 기반 요청 제한**: 하루 3회 분석 제한

## 기술 스택

- **Backend**: Django 5.x
- **AI**: OpenAI API, Anthropic API
- **PDF 파싱**: PyMuPDF
- **Database**: SQLite3
- **Frontend**: Bootstrap 5, Marked.js

## 설치 및 실행

### 1. 저장소 클론

```bash
git clone <repository-url>
cd resume-evaluation
```

### 2. 가상환경 생성 및 활성화

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정

```bash
# 필수: AI API 키 (둘 중 하나 이상)
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# 선택: 운영 환경 설정
export DJANGO_SECRET_KEY="your-production-secret-key"
export DJANGO_DEBUG="False"
```

### 5. 데이터베이스 마이그레이션

```bash
python manage.py migrate
```

### 6. 서버 실행

```bash
python manage.py runserver
```

서버 실행 후 http://127.0.0.1:8000 접속

## 프로젝트 구조

```
resume-evaluation/
├── config/                 # Django 프로젝트 설정
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── evaluator/              # 메인 애플리케이션
│   ├── templates/          # HTML 템플릿
│   ├── forms.py            # 입력 폼
│   ├── views.py            # 뷰 로직
│   ├── models.py           # DB 모델 (요청 제한)
│   ├── file_parser.py      # 파일 파싱 (PDF/MD/TXT)
│   └── urls.py             # URL 라우팅
├── prompt/
│   └── prompt.md           # AI 시스템 프롬프트
├── llm_client.py           # LLM API 클라이언트
├── manage.py
└── requirements.txt
```

## 환경변수

| 변수명 | 필수 | 설명 | 기본값 |
|--------|------|------|--------|
| `OPENAI_API_KEY` | △ | OpenAI API 키 | - |
| `ANTHROPIC_API_KEY` | △ | Anthropic API 키 | - |
| `DJANGO_SECRET_KEY` | ✕ | Django 시크릿 키 | 개발용 키 |
| `DJANGO_DEBUG` | ✕ | 디버그 모드 | True |

> △: 둘 중 하나 이상 필요

## 운영 배포

### 도메인 설정

`config/settings.py`에 도메인이 설정되어 있습니다:

```python
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "fitup.harubuild.xyz",
]

CSRF_TRUSTED_ORIGINS = [
    "https://fitup.harubuild.xyz",
]
```

### 정적 파일 수집

```bash
python manage.py collectstatic
```

### Gunicorn 실행 예시

```bash
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

## 요청 제한

- IP당 하루 3회 분석 가능
- 자정(Asia/Seoul) 기준 초기화
- 분석 성공 시에만 카운트 차감

## 라이선스

MIT License
