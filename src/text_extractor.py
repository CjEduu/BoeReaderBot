"""Text extraction module for various file formats."""

from pathlib import Path

from pypdf import PdfReader


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
    return _extract_from_xml(path)

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
