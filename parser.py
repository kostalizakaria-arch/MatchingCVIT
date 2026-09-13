from pathlib import Path
from pypdf import PdfReader
from docx import Document

def extract_text(path: str) -> str:
    p = Path(path)
    if p.suffix.lower() == ".pdf":
        reader = PdfReader(str(p))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if p.suffix.lower() == ".docx":
        doc = Document(str(p))
        return "\n".join(par.text for par in doc.paragraphs)
    if p.suffix.lower() == ".txt":
        return p.read_text(encoding="utf-8", errors="ignore")
    raise ValueError(f"Format non supporté: {p.suffix}")
