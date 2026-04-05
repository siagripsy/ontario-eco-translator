from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

from app.utils.text import normalize_whitespace


@dataclass(slots=True)
class ExtractedPage:
    page_number: int
    text: str


class PDFTextExtractor:
    def extract_pages(self, file_path: Path) -> list[ExtractedPage]:
        reader = PdfReader(str(file_path))
        pages: list[ExtractedPage] = []

        for index, page in enumerate(reader.pages, start=1):
            text = normalize_whitespace(page.extract_text() or "")
            if text:
                pages.append(ExtractedPage(page_number=index, text=text))

        return pages
