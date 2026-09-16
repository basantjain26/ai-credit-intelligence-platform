from __future__ import annotations

import psycopg2

from src.settings import DB_CONFIG

from src.document_intelligence.index_text_document import (
    TextDocumentIndexer,
)


POLICY_DOCUMENT_NAME = (
    "Commercial_Lending_Policy_2026.txt"
)


def get_policy_document_id() -> str:

    connection = psycopg2.connect(
        **DB_CONFIG
    )

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT document_id
                FROM documents
                WHERE document_name = %s
                  AND document_type = 'LENDING_POLICY'
                  AND customer_id IS NULL
                  AND application_id IS NULL
                """,
                (POLICY_DOCUMENT_NAME,),
            )

            row = cursor.fetchone()

    finally:
        connection.close()

    if row is None:
        raise RuntimeError(
            "Enterprise lending policy "
            "document was not found."
        )

    return row[0]


def main() -> None:

    document_id = get_policy_document_id()

    print(
        f"Policy document ID: {document_id}"
    )

    indexer = TextDocumentIndexer()

    indexer.index(
        document_id=document_id
    )


if __name__ == "__main__":
    main()