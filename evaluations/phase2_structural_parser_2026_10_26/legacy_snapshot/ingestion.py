"""Bounded, in-memory parsing of user documents. No macros or external links run."""
from io import BytesIO
from pathlib import PurePath
import zipfile
from defusedxml import ElementTree
from fastapi import HTTPException

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_TEXT_CHARS = 250_000
MAX_PDF_PAGES = 100


def parse_document(content: bytes, filename: str) -> str:
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "File exceeds the 10 MB limit.")
    extension = PurePath(filename).suffix.lower()
    if extension not in {".txt", ".pdf", ".docx"}:
        raise HTTPException(415, "Supported formats are PDF, DOCX and UTF-8 TXT.")
    try:
        if extension == ".txt":
            text = content.decode("utf-8-sig")
            if "\x00" in text:
                raise ValueError("Binary data in text file")
        elif extension == ".pdf":
            import pdfplumber
            if not content.startswith(b"%PDF-"):
                raise ValueError("Invalid PDF signature")
            with pdfplumber.open(BytesIO(content)) as pdf:
                if len(pdf.pages) > MAX_PDF_PAGES:
                    raise HTTPException(413, "PDF exceeds the 100 page limit.")
                parts, size = [], 0
                for page in pdf.pages:
                    part = page.extract_text() or ""
                    size += len(part)
                    if size > MAX_TEXT_CHARS:
                        raise HTTPException(413, "Extracted text exceeds 250,000 characters.")
                    parts.append(part)
                    page.close()
                text = "\n\n".join(parts)
        else:
            with zipfile.ZipFile(BytesIO(content)) as archive:
                entries = archive.infolist()
                if len(entries) > 2000 or sum(e.file_size for e in entries) > 25 * 1024 * 1024:
                    raise HTTPException(413, "DOCX archive exceeds safe parsing limits.")
                names = [e.filename for e in entries]
                if len(names) != len(set(names)) or "word/document.xml" not in names:
                    raise ValueError("Invalid DOCX archive")
                root = ElementTree.fromstring(archive.read("word/document.xml"))
                ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
                text = "\n".join("".join(p.itertext()) for p in root.findall(".//w:p", ns))
    except HTTPException:
        raise
    except ImportError:
        raise HTTPException(503, "Document parser unavailable. Install the release requirements.")
    except Exception:
        raise HTTPException(400, "File is damaged, encrypted, or invalid for its format. TXT must be UTF-8.")
    if not text.strip():
        raise HTTPException(400, "No readable text found. Empty or scanned documents require text extraction or OCR first.")
    if len(text) > MAX_TEXT_CHARS:
        raise HTTPException(413, "Extracted text exceeds 250,000 characters.")
    return text
