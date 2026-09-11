import json
import psycopg2

from src.document_intelligence.models import ExtractedDocument
from src.settings import DB_CONFIG

# DB_CONFIG = {
#     "host": "127.0.0.1",
#     "port": 5434,
#     "dbname": "credit_intelligence",
#     "user": "credit_user",
#     "password": "credit_password",
# }


class ExtractionRepository:

    def save(self, document: ExtractedDocument) -> None:

        connection = psycopg2.connect(**DB_CONFIG)

        try:
            with connection:
                with connection.cursor() as cursor:

                    # Makes re-processing idempotent.
                    cursor.execute(
                        """
                        DELETE FROM document_content_blocks
                        WHERE document_id = %s
                        """,
                        (document.document_id,),
                    )

                    for block in document.content_blocks:

                        table_content = (
                            json.dumps(block.rows)
                            if block.rows is not None
                            else None
                        )

                        cursor.execute(
                            """
                            INSERT INTO document_content_blocks (
                                block_id,
                                document_id,
                                block_type,
                                text_content,
                                table_content,
                                page_number,
                                paragraph_index,
                                table_index,
                                sheet_name,
                                row_number,
                                parser_name,
                                parser_version
                            )
                            VALUES (
                                %s, %s, %s, %s,
                                %s::jsonb,
                                %s, %s, %s, %s, %s,
                                %s, %s
                            )
                            """,
                            (
                                block.block_id,
                                document.document_id,
                                block.block_type,
                                block.text,
                                table_content,
                                block.page_number,
                                block.paragraph_index,
                                block.table_index,
                                block.sheet_name,
                                block.row_number,
                                document.parser_name,
                                document.parser_version,
                            ),
                        )

                    cursor.execute(
                        """
                        UPDATE documents
                        SET processing_status = 'EXTRACTED'
                        WHERE document_id = %s
                        """,
                        (document.document_id,),
                    )

        finally:
            connection.close()