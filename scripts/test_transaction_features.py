from datetime import datetime
from pprint import pprint

from src.transaction_investigation.feature_engineering import (
    ML_FEATURES,
    TransactionFeatureEngineer,
)


def main():

    transactions = [
        {
            "transaction_id": "TXN_001",
            "transaction_timestamp": datetime(
                2026,
                6,
                1,
                10,
                0,
            ),
            "transaction_type": "CREDIT",
            "amount": 3_000_000,
            "counterparty_name": "Customer A",
            "description": "Customer payment",
        },
        {
            "transaction_id": "TXN_002",
            "transaction_timestamp": datetime(
                2026,
                6,
                3,
                11,
                30,
            ),
            "transaction_type": "DEBIT",
            "amount": 2_500_000,
            "counterparty_name": "Supplier A",
            "description": "Supplier payment",
        },
        {
            "transaction_id": "TXN_003",
            "transaction_timestamp": datetime(
                2026,
                6,
                5,
                14,
                0,
            ),
            "transaction_type": "DEBIT",
            "amount": 10_000_000,
            "counterparty_name": "XYZ Holdings Pvt Ltd",
            "description": "Intercompany transfer",
        },
        {
            "transaction_id": "TXN_004",
            "transaction_timestamp": datetime(
                2026,
                6,
                7,
                14,
                15,
            ),
            "transaction_type": "DEBIT",
            "amount": 10_000_000,
            "counterparty_name": "XYZ Holdings Pvt Ltd",
            "description": "Intercompany transfer",
        },
        {
            "transaction_id": "TXN_005",
            "transaction_timestamp": datetime(
                2026,
                6,
                12,
                9,
                45,
            ),
            "transaction_type": "DEBIT",
            "amount": 37_800_000,
            "counterparty_name": "XYZ Holdings Pvt Ltd",
            "description": "Intercompany settlement",
        },
        {
            "transaction_id": "TXN_006",
            "transaction_timestamp": datetime(
                2026,
                6,
                18,
                16,
                20,
            ),
            "transaction_type": "DEBIT",
            "amount": 16_500_000,
            "counterparty_name": (
                "Orion Global Trading LLC"
            ),
            "description": (
                "International supplier payment"
            ),
        },
    ]

    related_parties = {
        "XYZ Holdings Pvt Ltd",
    }

    engineer = (
        TransactionFeatureEngineer()
    )

    feature_rows = (
        engineer.transform(
            transactions=transactions,
            related_party_names=(
                related_parties
            ),
        )
    )

    print(
        "\nML FEATURES"
    )

    print(
        ML_FEATURES
    )

    print(
        "\n"
        + "=" * 80
    )

    print(
        "ENGINEERED TRANSACTIONS"
    )

    print(
        "=" * 80
    )

    for row in feature_rows:

        print(
            "\nTransaction:",
            row[
                "transaction_id"
            ],
        )

        print(
            "Counterparty:",
            row[
                "counterparty_name"
            ],
        )

        print(
            "Amount:",
            row[
                "amount"
            ],
        )

        print(
            "ML features:"
        )

        pprint(
            {
                feature: row[
                    feature
                ]
                for feature
                in ML_FEATURES
            }
        )

        print(
            "Rule features:",
            {
                "is_round_amount": (
                    row[
                        "is_round_amount"
                    ]
                ),
                "is_related_party": (
                    row[
                        "is_related_party"
                    ]
                ),
            },
        )

    matrix = (
        engineer.get_ml_matrix(
            feature_rows
        )
    )

    print(
        "\n"
        + "=" * 80
    )

    print(
        "ISOLATION FOREST MATRIX"
    )

    print(
        "=" * 80
    )

    print(
        "Columns:"
    )

    print(
        ML_FEATURES
    )

    for row in matrix:
        print(
            row
        )


if __name__ == "__main__":
    main()