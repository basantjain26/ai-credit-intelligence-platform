from pathlib import Path
import json

from src.document_intelligence.extractors.docx import DOCXExtractor


def main():
    file_path = Path(
        "data/source/documents/"
        "borrower_profiles/"
        "ABC_Borrower_Profile_and_Credit_Note.docx"
    )

    extractor = DOCXExtractor()

    result = extractor.extract(
        file_path=file_path,
        document_id="TEST_DOC_002",
    )

    print(
        json.dumps(
            result,
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()