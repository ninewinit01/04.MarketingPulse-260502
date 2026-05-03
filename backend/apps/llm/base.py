"""LLM provider 추상 인터페이스 (Phase 2 활성화)."""
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def summarize(self, text: str, max_tokens: int = 200) -> str: ...

    @abstractmethod
    def classify_industry(self, text: str, industries: list[str]) -> list[str]: ...
