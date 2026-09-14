from pprint import pprint

from src.borrower_intelligence.tools import (
    BorrowerTools,
)


def main():

    tools = BorrowerTools(
        customer_id="CUST_000001",
        application_id="APP_2026_00001",
    )

    try:

        print(
            "\n========== BORROWER PROFILE ==========\n"
        )

        pprint(
            tools.get_borrower_profile()
        )

        print(
            "\n========== APPLICATION ==========\n"
        )

        pprint(
            tools.get_application_details()
        )

        print(
            "\n========== EXPOSURE ==========\n"
        )

        pprint(
            tools.get_existing_exposure()
        )

        print(
            "\n========== DIRECTORS ==========\n"
        )

        pprint(
            tools.get_directors()
        )

        print(
            "\n========== RELATED PARTIES ==========\n"
        )

        pprint(
            tools.get_related_parties()
        )

        print(
            "\n========== BORROWER SIGNALS ==========\n"
        )

        pprint(
            tools.get_borrower_signals()
        )

        print(
            "\n========== DOCUMENT SEARCH ==========\n"
        )

        pprint(
            tools.search_borrower_documents(
                query=(
                    "What was FY2026 revenue?"
                ),
                limit=3,
            )
        )

    finally:

        tools.close()


if __name__ == "__main__":
    main()