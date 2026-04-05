from dataclasses import dataclass

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import get_settings


@dataclass(slots=True)
class ChunkCandidate:
    chunk_index: int
    chunk_text: str
    page_number: int | None
    section_title: str | None


class TariffChunkingService:
    def __init__(self) -> None:
        settings = get_settings()
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", ". ", " "],
        )

    def chunk_pages(self, pages: list) -> list[ChunkCandidate]:
        chunks: list[ChunkCandidate] = []
        next_index = 0

        for page in pages:
            section_title = self._extract_section_title(page.text)
            for chunk_text in self.splitter.split_text(page.text):
                chunks.append(
                    ChunkCandidate(
                        chunk_index=next_index,
                        chunk_text=chunk_text.strip(),
                        page_number=page.page_number,
                        section_title=section_title,
                    )
                )
                next_index += 1

        return chunks

    @staticmethod
    def _extract_section_title(page_text: str) -> str | None:
        for line in page_text.splitlines():
            cleaned = line.strip()
            if 3 <= len(cleaned) <= 120:
                return cleaned
        return None
