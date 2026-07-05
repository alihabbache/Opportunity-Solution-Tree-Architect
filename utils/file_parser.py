"""
File parser utility.
Accepts .md, .docx, and .pdf files and returns clean plain text.
All agents receive a uniform string regardless of the original format.
"""

import os
import pathlib

# Reject files larger than 5 MB to guard against zip-bomb / DoS inputs
MAX_FILE_BYTES = 5 * 1024 * 1024  # 5 MB


def parse_file(filepath: str) -> str:
    """
    Parse a file and return its content as plain text.

    Supported formats: .md, .txt, .docx, .pdf

    Args:
        filepath: Absolute or relative path to the file.

    Returns:
        Plain text content of the file.

    Raises:
        ValueError: If the file format is not supported.
        FileNotFoundError: If the file does not exist.
    """
    path = pathlib.Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    if path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError(
            f"File too large: {path.name} ({path.stat().st_size:,} bytes). "
            f"Maximum allowed size is {MAX_FILE_BYTES // (1024 * 1024)} MB."
        )

    suffix = path.suffix.lower()

    if suffix in (".md", ".txt"):
        return _parse_text(path)
    elif suffix == ".docx":
        return _parse_docx(path)
    elif suffix == ".pdf":
        return _parse_pdf(path)
    else:
        raise ValueError(
            f"Unsupported file format: '{suffix}'. "
            f"Supported formats: .md, .txt, .docx, .pdf"
        )


def parse_directory(directory: str, recursive: bool = True) -> str:
    """
    Parse all supported files in a directory and concatenate their contents.

    Args:
        directory: Path to the directory.
        recursive: Whether to recurse into subdirectories.

    Returns:
        Concatenated plain text from all supported files.
    """
    dir_path = pathlib.Path(directory)

    if not dir_path.exists() or not dir_path.is_dir():
        return ""

    supported = {".md", ".txt", ".docx", ".pdf"}
    texts = []

    pattern = "**/*" if recursive else "*"
    for file_path in sorted(dir_path.glob(pattern)):
        if file_path.is_file() and file_path.suffix.lower() in supported:
            try:
                content = parse_file(str(file_path))
                if content.strip():
                    texts.append(f"--- {file_path.name} ---\n{content}")
                    print(f"[file_parser] Parsed: {file_path.name}")
            except MemoryError:
                raise
            except Exception as e:
                print(f"[file_parser] Warning: Could not parse {file_path.name}: {e}")

    return "\n\n".join(texts)


# ── Private parsers ────────────────────────────────────────────────────────────

def _parse_text(path: pathlib.Path) -> str:
    """Read a plain text or Markdown file."""
    for encoding in ("utf-8", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(f"Could not decode {path} with utf-8 or latin-1.")


def _parse_docx(path: pathlib.Path) -> str:
    """Extract text from a Word .docx file."""
    try:
        from docx import Document
    except ImportError:
        raise ImportError("python-docx is required to parse .docx files. Run: pip install python-docx")

    doc = Document(str(path))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def _parse_pdf(path: pathlib.Path) -> str:
    """Extract text from a PDF file."""
    try:
        from pypdf import PdfReader
    except ImportError:
        raise ImportError("pypdf is required to parse .pdf files. Run: pip install pypdf")

    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text and text.strip():
            pages.append(text)
    return "\n".join(pages)
