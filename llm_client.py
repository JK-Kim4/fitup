"""LLM Client module supporting Claude and OpenAI APIs."""

import os
from abc import ABC, abstractmethod


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    def generate(self, system_prompt: str, user_message: str) -> str:
        """Generate a response from the LLM."""
        pass


class ClaudeClient(LLMClient):
    """Anthropic Claude API client."""

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError("anthropic 패키지가 필요합니다: pip install anthropic")

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY 환경변수를 설정해주세요.")

        self.client = Anthropic(api_key=api_key)
        self.model = model

    def generate(self, system_prompt: str, user_message: str) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=8192,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text


class OpenAIClient(LLMClient):
    """OpenAI API client."""

    # 모델별 max_tokens 제한
    MAX_TOKENS_MAP = {
        "gpt-4o": 16384,
        "gpt-4o-mini": 16384,
        "gpt-4-turbo": 4096,
        "gpt-4": 8192,
        "gpt-3.5-turbo": 4096,
    }

    def __init__(self, model: str = "gpt-4o"):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai 패키지가 필요합니다: pip install openai")

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY 환경변수를 설정해주세요.")

        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.max_tokens = self.MAX_TOKENS_MAP.get(model, 4096)

    def generate(self, system_prompt: str, user_message: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return response.choices[0].message.content


def get_client(provider: str, model: str = None) -> LLMClient:
    """Get an LLM client based on the provider.

    Args:
        provider: 'claude' or 'openai'
        model: Optional model name override

    Returns:
        LLMClient instance
    """
    if provider == "claude":
        return ClaudeClient(model=model) if model else ClaudeClient()
    elif provider == "openai":
        return OpenAIClient(model=model) if model else OpenAIClient()
    else:
        raise ValueError(f"지원하지 않는 provider입니다: {provider}")
