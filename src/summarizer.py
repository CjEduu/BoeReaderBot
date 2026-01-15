"""Summarization module with interchangeable model support."""

import os
from abc import ABC, abstractmethod

import google.generativeai as genai


DEFAULT_SYSTEM_PROMPT = """You are a document summarizer. Create a concise summary of the provided text.

Requirements:
- Keep the summary brief and scannable for mobile reading
- Use bullet points for key information
- Highlight the most important facts and dates
- Format for Telegram (use simple markdown: *bold*, _italic_)
- Maximum 500 words
- Write in the same language as the source document
"""


def get_system_prompt() -> str:
    """Get system prompt from environment or use default."""
    return os.getenv("SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT)


class BaseSummarizer(ABC):
    """Abstract base class for summarizers."""

    @abstractmethod
    def summarize(self, text: str) -> str:
        """
        Generate a summary of the provided text.

        Args:
            text: The text to summarize.

        Returns:
            A concise summary of the text.
        """
        pass


class GeminiSummarizer(BaseSummarizer):
    """Summarizer using Google's Gemini API."""

    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-1.5-flash",
        system_prompt: str | None = None,
    ) -> None:
        """
        Initialize the Gemini summarizer.

        Args:
            api_key: Google AI API key.
            model_name: The Gemini model to use.
            system_prompt: Custom system prompt (uses env/default if None).
        """
        genai.configure(api_key=api_key)
        prompt = system_prompt if system_prompt is not None else get_system_prompt()
        self.model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=prompt,
        )

    def summarize(self, text: str) -> str:
        """
        Generate a summary using Gemini.

        Args:
            text: The text to summarize.

        Returns:
            A concise summary of the text.

        Raises:
            RuntimeError: If the API call fails.
        """
        try:
            response = self.model.generate_content(
                f"Please summarize the following document:\n\n{text}"
            )
            return response.text
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {e}") from e


def create_summarizer(
    api_key: str,
    model_type: str = "gemini",
    system_prompt: str | None = None,
) -> BaseSummarizer:
    """
    Factory function to create a summarizer instance.

    Args:
        api_key: API key for the model service.
        model_type: Type of summarizer to create ("gemini").
        system_prompt: Custom system prompt (uses SYSTEM_PROMPT env var or default if None).

    Returns:
        A summarizer instance.

    Raises:
        ValueError: If the model type is not supported.
    """
    if model_type == "gemini":
        return GeminiSummarizer(api_key, system_prompt=system_prompt)
    else:
        raise ValueError(f"Unsupported model type: {model_type}")
