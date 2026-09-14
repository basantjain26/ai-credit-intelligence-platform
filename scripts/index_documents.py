from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor

from src.document_intelligence.index_document import (
    DocumentIndexer,
)
from src.settings import DB_CONFIG


def get_documents_to_index() -> list[dict]:
    connection = psycopg2.connect(**DB_CONFIG)

    try:
        with connection.cursor(
            cursor_factory=RealDictCursor
        ) as cursor:
            cursor.execute(
                """
                SELECT
                    document_id,
                    document_name,
                    source_path,
                    file_format,
                    customer_id,
                    application_id
                FROM documents
                WHERE processing_status = 'EXTRACTED' AND LOWER(file_format) = 'pdf'
                ORDER BY created_at;
                """
            )

            return [
                dict(row)
                for row in cursor.fetchall()
            ]

    finally:
        connection.close()


def main():
    documents = get_documents_to_index()

    print(
        f"Found {len(documents)} documents to index."
    )

    indexer = DocumentIndexer()

    for document in documents:
        file_path = Path(
            document["source_path"]
        )

        print(
            "\n===================================="
        )

        print(
            "Indexing:",
            document["document_name"],
        )

        print(
            "Document ID:",
            document["document_id"],
        )

        print(
            "Path:",
            file_path,
        )

        if not file_path.exists():
            print(
                "SKIPPED: source file does not exist."
            )
            continue

        try:
            indexer.index_pdf(
                document_id=document["document_id"],
                file_path=file_path,
            )

            print(
                "SUCCESS"
            )

        except Exception as exc:
            print(
                "FAILED:",
                repr(exc),
            )


if __name__ == "__main__":
    main()