"""Text extraction module for various file formats."""

from pathlib import Path

from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {".pdf", ".xml"}


def extract_text(file_path: str | Path) -> str:
    """
    Extract text content from a supported file.

    Args:
        file_path: Path to the file.

    Returns:
        Extracted text content.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file type is not supported or file is empty.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    suffix = path.suffix.lower()

    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {suffix}. "
            f"Supported types: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    if suffix == ".pdf":
        return _extract_from_pdf(path)
    elif suffix == ".xml":
        return _extract_from_xml(path)

    # This should never be reached, but satisfies type checker
    raise ValueError(f"Unhandled file type: {suffix}")


def _extract_from_pdf(path: Path) -> str:
    """Extract text from a PDF file."""
    reader = PdfReader(path)

    if len(reader.pages) == 0:
        raise ValueError(f"PDF file is empty: {path}")

    text_parts: list[str] = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            # Handle basic encoding issues by normalizing whitespace
            cleaned_text = " ".join(page_text.split())
            text_parts.append(cleaned_text)

    full_text = "\n\n".join(text_parts)

    if not full_text.strip():
        raise ValueError(f"Could not extract any text from PDF: {path}")

    return full_text


def _extract_from_xml(path: Path) -> str:
    """
    Extract text from an XML file.

    XML files are read directly as text without preprocessing.
    """
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # Fallback to latin-1 if utf-8 fails
        content = path.read_text(encoding="latin-1")

    if not content.strip():
        raise ValueError(f"XML file is empty: {path}")

    return content
