"""Tests for BOE Resumer."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pdf_extractor import extract_text_from_pdf
from summarizer import BaseSummarizer, GeminiSummarizer, create_summarizer
from telegram_sender import send_telegram_message, _split_message


class TestPDFExtractor:
    """Tests for PDF extraction module."""

    def test_extract_text_file_not_found(self) -> None:
        """Test that FileNotFoundError is raised for missing files."""
        with pytest.raises(FileNotFoundError):
            extract_text_from_pdf("/nonexistent/path/file.pdf")

    def test_extract_text_invalid_extension(self, tmp_path: Path) -> None:
        """Test that ValueError is raised for non-PDF files."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("Not a PDF")

        with pytest.raises(ValueError, match="not a PDF"):
            extract_text_from_pdf(txt_file)


class TestSummarizer:
    """Tests for summarization module."""

    def test_base_summarizer_is_abstract(self) -> None:
        """Test that BaseSummarizer cannot be instantiated."""
        with pytest.raises(TypeError):
            BaseSummarizer()  # type: ignore

    def test_create_summarizer_gemini(self) -> None:
        """Test factory creates GeminiSummarizer."""
        with patch("summarizer.genai"):
            summarizer = create_summarizer("fake-api-key", "gemini")
            assert isinstance(summarizer, GeminiSummarizer)

    def test_create_summarizer_unsupported(self) -> None:
        """Test factory raises error for unsupported model."""
        with pytest.raises(ValueError, match="Unsupported model type"):
            create_summarizer("fake-api-key", "unsupported")

    def test_gemini_summarizer_summarize(self) -> None:
        """Test GeminiSummarizer.summarize returns expected output."""
        with patch("summarizer.genai") as mock_genai:
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "This is a test summary."
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model

            summarizer = GeminiSummarizer("fake-api-key")
            result = summarizer.summarize("Test document content.")

            assert result == "This is a test summary."
            mock_model.generate_content.assert_called_once()


class TestTelegramSender:
    """Tests for Telegram integration module."""

    def test_send_telegram_message_success(self) -> None:
        """Test successful message sending."""
        with patch("telegram_sender.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"ok": True}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            result = send_telegram_message(
                bot_token="fake-token",
                chat_id="12345",
                message="Test message",
            )

            assert result is True
            mock_post.assert_called_once()

    def test_send_telegram_message_api_error(self) -> None:
        """Test API error handling."""
        with patch("telegram_sender.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "ok": False,
                "description": "Bad Request",
            }
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            with pytest.raises(RuntimeError, match="Telegram API error"):
                send_telegram_message(
                    bot_token="fake-token",
                    chat_id="12345",
                    message="Test message",
                )

    def test_split_message(self) -> None:
        """Test message splitting for long messages."""
        long_message = "Line 1\n" * 100
        chunks = _split_message(long_message, max_length=50)

        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk) <= 50


class TestTyping:
    """Tests for type annotations."""

    def test_extract_text_accepts_path_object(self, tmp_path: Path) -> None:
        """Test that extract_text_from_pdf accepts Path objects."""
        # This tests the Union[str, Path] type hint
        pdf_path = tmp_path / "test.pdf"
        # File doesn't exist, but we're testing the type acceptance
        with pytest.raises(FileNotFoundError):
            extract_text_from_pdf(pdf_path)

    def test_summarizer_type_hint(self) -> None:
        """Test that summarizer factory returns correct type."""
        with patch("summarizer.genai"):
            summarizer = create_summarizer("key", "gemini")
            # Type check: should be BaseSummarizer
            assert isinstance(summarizer, BaseSummarizer)
