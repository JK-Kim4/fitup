"""File parser module for extracting text from various file formats."""

import io
from pathlib import Path


def parse_pdf(file) -> str:
    """Extract text from a PDF file."""
    import fitz  # PyMuPDF

    # 파일 객체에서 바이트 읽기
    if hasattr(file, 'read'):
        pdf_bytes = file.read()
        if hasattr(file, 'seek'):
            file.seek(0)  # 파일 포인터 리셋
    else:
        pdf_bytes = file

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text_parts = []

    for page in doc:
        text_parts.append(page.get_text())

    doc.close()
    return "\n".join(text_parts)


def parse_markdown(file) -> str:
    """Extract text from a Markdown file."""
    if hasattr(file, 'read'):
        content = file.read()
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        if hasattr(file, 'seek'):
            file.seek(0)
        return content
    return file.decode('utf-8') if isinstance(file, bytes) else file


def parse_text(file) -> str:
    """Extract text from a plain text file."""
    if hasattr(file, 'read'):
        content = file.read()
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        if hasattr(file, 'seek'):
            file.seek(0)
        return content
    return file.decode('utf-8') if isinstance(file, bytes) else file


def parse_file(uploaded_file) -> str:
    """Parse an uploaded file and extract text content.

    Supports: PDF, Markdown (.md), Text (.txt)

    Args:
        uploaded_file: Django UploadedFile object

    Returns:
        Extracted text content
    """
    filename = uploaded_file.name.lower()

    if filename.endswith('.pdf'):
        return parse_pdf(uploaded_file)
    elif filename.endswith('.md') or filename.endswith('.markdown'):
        return parse_markdown(uploaded_file)
    elif filename.endswith('.txt'):
        return parse_text(uploaded_file)
    else:
        # 기본적으로 텍스트로 시도
        try:
            return parse_text(uploaded_file)
        except Exception:
            raise ValueError(f"지원하지 않는 파일 형식입니다: {filename}")
