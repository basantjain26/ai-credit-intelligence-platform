from abc import ABC, abstractmethod
from pathlib import Path


class DocumentExtractor(ABC):

    @abstractmethod
    def extract(self, file_path: Path, document_id: str) -> dict:
        pass