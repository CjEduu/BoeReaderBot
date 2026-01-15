"""PDF text extraction module."""

from pathlib import Path

from pypdf import PdfReader


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    """
    Extract text content from a PDF file.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Extracted text content from all pages.

    Raises:
        FileNotFoundError: If the PDF file does not exist.
        ValueError: If the file is not a valid PDF or is empty.
    """
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {path}")

    if not path.suffix.lower() == ".pdf":
        raise ValueError(f"File is not a PDF: {path}")

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
