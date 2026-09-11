from pathlib import Path
import hashlib
import uuid
import psycopg2


SOURCE_ROOT = Path("data/source/documents")

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5434,
    "dbname": "credit_intelligence",
    "user": "credit_user",
    "password": "credit_password",
}


SUPPORTED_FORMATS = {
    ".pdf",
    ".docx",
    ".xlsx",
    ".csv",
    ".json",
}


def calculate_sha256(file_path: Path) -> str:
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while chunk := file.read(8192):
            sha256.update(chunk)

    return sha256.hexdigest()


def infer_document_type(file_path: Path) -> str:
    folder = file_path.parent.name

    mapping = {
        "financial_statements": "FINANCIAL_STATEMENT",
        "borrower_profiles": "BORROWER_PROFILE",
        "exposure_schedules": "EXPOSURE_SCHEDULE",
        "transaction_extracts": "TRANSACTION_EXTRACT",
        "credit_bureau": "CREDIT_BUREAU_REPORT",
    }

    return mapping.get(folder, "UNKNOWN")


def discover_documents():
    documents = []

    for file_path in SOURCE_ROOT.rglob("*"):

        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in SUPPORTED_FORMATS:
            continue

        document = {
            "document_id": f"DOC_{uuid.uuid4().hex[:12].upper()}",
            "customer_id": "CUST_000001",
            "application_id": "APP_2026_00001",
            "document_type": infer_document_type(file_path),
            "document_name": file_path.name,
            "file_format": file_path.suffix.lower().replace(".", "").upper(),
            "source_path": str(file_path),
            "file_size_bytes": file_path.stat().st_size,
            "checksum_sha256": calculate_sha256(file_path),
        }

        documents.append(document)

    return documents


def register_documents(documents):

    connection = psycopg2.connect(**DB_CONFIG)

    try:
        with connection:
            with connection.cursor() as cursor:

                for document in documents:

                    cursor.execute(
                        """
                        INSERT INTO documents (
                            document_id,
                            customer_id,
                            application_id,
                            document_type,
                            document_name,
                            file_format,
                            source_path,
                            file_size_bytes,
                            checksum_sha256,
                            processing_status
                        )
                        VALUES (
                            %(document_id)s,
                            %(customer_id)s,
                            %(application_id)s,
                            %(document_type)s,
                            %(document_name)s,
                            %(file_format)s,
                            %(source_path)s,
                            %(file_size_bytes)s,
                            %(checksum_sha256)s,
                            'INGESTED'
                        )
                        ON CONFLICT (checksum_sha256)
                        DO NOTHING;
                        """,
                        document,
                    )

                    print(
                        f"Registered: "
                        f"{document['document_name']} "
                        f"[{document['document_type']}]"
                    )

    finally:
        connection.close()


def main():

    documents = discover_documents()

    print(f"Discovered {len(documents)} documents")

    register_documents(documents)


if __name__ == "__main__":
    main()