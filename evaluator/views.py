"""Views for the resume evaluator."""

import os
import sys
from pathlib import Path

from django.shortcuts import render
from django.views import View

from .forms import EvaluationForm
from .file_parser import parse_file
from .models import RequestLog

# 프로젝트 루트 디렉토리
BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_PATH = BASE_DIR / "prompt" / "prompt.md"

# llm_client 모듈을 임포트할 수 있도록 경로 추가
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# 일일 요청 제한
DAILY_REQUEST_LIMIT = 3


def get_client_ip(request) -> str:
    """클라이언트 IP 주소를 반환합니다."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def load_system_prompt() -> str:
    """Load the system prompt from file."""
    return PROMPT_PATH.read_text(encoding="utf-8")


def build_user_message(jd: str, resume: str, career_description: str = None) -> str:
    """Build the user message for the LLM."""
    message = f"""아래 채용공고(JD)와 이력서를 분석해주세요.

## 채용공고 (JD)
{jd}

## 이력서
{resume}
"""

    if career_description:
        message += f"""
## 경력기술서
{career_description}
"""

    return message


class EvaluationView(View):
    """Main evaluation view."""

    template_name = "evaluator/index.html"

    def get_context_data(self, request, **kwargs):
        """공통 컨텍스트 데이터를 반환합니다."""
        ip_address = get_client_ip(request)
        remaining = RequestLog.get_remaining_requests(ip_address, DAILY_REQUEST_LIMIT)
        return {
            "remaining_requests": remaining,
            "daily_limit": DAILY_REQUEST_LIMIT,
            **kwargs,
        }

    def get(self, request):
        """Display the evaluation form."""
        form = EvaluationForm()
        context = self.get_context_data(request, form=form)
        return render(request, self.template_name, context)

    def post(self, request):
        """Process the evaluation request."""
        ip_address = get_client_ip(request)

        # 요청 제한 확인
        if not RequestLog.can_make_request(ip_address, DAILY_REQUEST_LIMIT):
            form = EvaluationForm()
            context = self.get_context_data(
                request,
                form=form,
                error="오늘의 분석 요청 한도(3회)를 초과했습니다. 내일 다시 이용해주세요.",
            )
            return render(request, self.template_name, context)

        form = EvaluationForm(request.POST, request.FILES)

        if not form.is_valid():
            context = self.get_context_data(request, form=form)
            return render(request, self.template_name, context)

        provider = form.cleaned_data["provider"]
        jd = form.cleaned_data["jd"]
        resume_file = form.cleaned_data["resume"]
        career_file = form.cleaned_data.get("career_description")

        # API 키 확인
        if provider == "openai" and not os.getenv("OPENAI_API_KEY"):
            context = self.get_context_data(
                request,
                form=form,
                error="OPENAI_API_KEY 환경변수가 설정되지 않았습니다.",
            )
            return render(request, self.template_name, context)
        elif provider == "claude" and not os.getenv("ANTHROPIC_API_KEY"):
            context = self.get_context_data(
                request,
                form=form,
                error="ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.",
            )
            return render(request, self.template_name, context)

        # 파일 파싱
        try:
            resume_text = parse_file(resume_file)
            career_text = parse_file(career_file) if career_file else None
        except Exception as e:
            context = self.get_context_data(
                request,
                form=form,
                error=f"파일 파싱 오류: {str(e)}",
            )
            return render(request, self.template_name, context)

        # LLM 클라이언트 임포트 및 실행
        try:
            from llm_client import get_client

            system_prompt = load_system_prompt()
            user_message = build_user_message(jd, resume_text, career_text)

            client = get_client(provider)
            result = client.generate(system_prompt, user_message)

            # 성공 시 요청 기록
            RequestLog.log_request(ip_address)

            context = self.get_context_data(
                request,
                form=EvaluationForm(),
                result=result,
            )
            return render(request, self.template_name, context)

        except Exception as e:
            context = self.get_context_data(
                request,
                form=form,
                error=f"분석 중 오류가 발생했습니다: {str(e)}",
            )
            return render(request, self.template_name, context)
