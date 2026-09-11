from pathlib import Path
import psycopg2

from src.document_intelligence.extractors.pdf import PDFExtractor
from src.document_intelligence.extractors.docx import DOCXExtractor
from src.document_intelligence.extractors.xlsx import XLSXExtractor
from src.document_intelligence.extractors.csv import CSVExtractor
from src.document_intelligence.extractors.json_file import JSONExtractor

from src.document_intelligence.repository import (
    ExtractionRepository,
    DB_CONFIG,
)
from src.settings import DB_CONFIG


EXTRACTORS = {
    "PDF": PDFExtractor(),
    "DOCX": DOCXExtractor(),
    "XLSX": XLSXExtractor(),
    "CSV": CSVExtractor(),
    "JSON": JSONExtractor(),
}


def get_documents():
    connection = psycopg2.connect(**DB_CONFIG)

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    document_id,
                    document_name,
                    file_format,
                    source_path
                FROM documents
                WHERE processing_status = 'CLASSIFIED'
                  AND file_format IN ('PDF', 'DOCX', 'XLSX', 'CSV', 'JSON')
                ORDER BY document_name
                """
            )

            return cursor.fetchall()

    finally:
        connection.close()


def main():

    repository = ExtractionRepository()

    for (
        document_id,
        document_name,
        file_format,
        source_path,
    ) in get_documents():

        extractor = EXTRACTORS[file_format]

        extracted_document = extractor.extract(
            file_path=Path(source_path),
            document_id=document_id,
        )

        repository.save(extracted_document)

        print(
            f"Extracted {document_name}: "
            f"{len(extracted_document.content_blocks)} blocks"
        )


if __name__ == "__main__":
    main()