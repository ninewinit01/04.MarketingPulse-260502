"""Claude provider — Phase 2 구현 예정.

settings.LLM_PROVIDER = "claude"
settings.LLM_API_KEY = "sk-ant-..."
"""
from apps.llm.base import LLMProvider


class ClaudeProvider(LLMProvider):
    def summarize(self, text: str, max_tokens: int = 200) -> str:
        raise NotImplementedError("Phase 2 — Claude API 연동 시 구현")

    def classify_industry(self, text: str, industries: list[str]) -> list[str]:
        raise NotImplementedError("Phase 2 — Claude API 연동 시 구현")
