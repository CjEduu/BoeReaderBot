"""Tests for BOE Resumer."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from text_extractor import extract_text, SUPPORTED_EXTENSIONS
from summarizer import BaseSummarizer, GeminiSummarizer, create_summarizer
from telegram_sender import send_telegram_message, _split_message


class TestTextExtractor:
    """Tests for text extraction module."""

    def test_extract_text_file_not_found(self) -> None:
        """Test that FileNotFoundError is raised for missing files."""
        with pytest.raises(FileNotFoundError):
            extract_text("/nonexistent/path/file.pdf")

    def test_extract_text_unsupported_extension(self, tmp_path: Path) -> None:
        """Test that ValueError is raised for unsupported file types."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("Not supported")

        with pytest.raises(ValueError, match="Unsupported file type"):
            extract_text(txt_file)

    def test_supported_extensions_includes_pdf_and_xml(self) -> None:
        """Test that both PDF and XML are in supported extensions."""
        assert ".pdf" in SUPPORTED_EXTENSIONS
        assert ".xml" in SUPPORTED_EXTENSIONS

    def test_extract_text_from_xml(self, tmp_path: Path) -> None:
        """Test XML text extraction."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<document>
    <title>Test Document</title>
    <content>This is test content.</content>
</document>"""
        xml_file = tmp_path / "test.xml"
        xml_file.write_text(xml_content)

        result = extract_text(xml_file)

        assert "Test Document" in result
        assert "This is test content." in result

    def test_extract_text_from_empty_xml(self, tmp_path: Path) -> None:
        """Test that ValueError is raised for empty XML files."""
        xml_file = tmp_path / "empty.xml"
        xml_file.write_text("   ")

        with pytest.raises(ValueError, match="XML file is empty"):
            extract_text(xml_file)


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
        """Test that extract_text accepts Path objects."""
        # This tests the Union[str, Path] type hint
        pdf_path = tmp_path / "test.pdf"
        # File doesn't exist, but we're testing the type acceptance
        with pytest.raises(FileNotFoundError):
            extract_text(pdf_path)

    def test_summarizer_type_hint(self) -> None:
        """Test that summarizer factory returns correct type."""
        with patch("summarizer.genai"):
            summarizer = create_summarizer("key", "gemini")
            # Type check: should be BaseSummarizer
            assert isinstance(summarizer, BaseSummarizer)
