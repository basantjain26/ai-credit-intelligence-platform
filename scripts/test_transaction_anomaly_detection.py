import os
from datetime import datetime

import psycopg2
from dotenv import load_dotenv

from src.transaction_investigation.anomaly_detection import (
    TransactionAnomalyDetector,
)

from src.transaction_investigation.feature_engineering import (
    ML_FEATURES,
    TransactionFeatureEngineer,
)


load_dotenv()


customer_id = "CUST_000001"
application_id = "APP_2026_00001"


TRAINING_END = datetime(
    2026,
    6,
    30,
    23,
    59,
    59,
)


def get_connection():

    return psycopg2.connect(
        host=os.getenv(
            "DB_HOST",
            "localhost",
        ),

        port=int(
            os.getenv(
                "DB_PORT",
                "5434",
            )
        ),

        dbname=os.getenv(
            "DB_NAME",
            "credit_intelligence",
        ),

        user=os.getenv(
            "DB_USER",
            "credit_user",
        ),

        password=os.getenv(
            "DB_PASSWORD",
            "credit_password",
        ),
    )


def load_transactions(
    connection,
) -> list[dict]:

    sql = """
        SELECT
            transaction_id,
            account_id,
            customer_id,
            transaction_timestamp,
            direction,
            transaction_type,
            amount,
            currency,
            counterparty_name,
            counterparty_account,
            counterparty_bank,
            merchant_category,
            country,
            channel,
            description,
            balance_after_transaction
        FROM bank_transactions
        WHERE customer_id = %s
        ORDER BY
            transaction_timestamp,
            transaction_id
    """

    with connection.cursor() as cursor:

        cursor.execute(
            sql,
            (customer_id,),
        )

        column_names = [
            description[0]
            for description
            in cursor.description
        ]

        rows = cursor.fetchall()

    return [
        dict(
            zip(
                column_names,
                row,
                strict=True,
            )
        )
        for row in rows
    ]


def split_transactions(
    transactions: list[dict],
) -> tuple[
    list[dict],
    list[dict],
]:

    training = []

    inference = []

    for transaction in transactions:

        timestamp = transaction[
            "transaction_timestamp"
        ]

        if timestamp <= TRAINING_END:
            training.append(
                transaction
            )
        else:
            inference.append(
                transaction
            )

    return (
        training,
        inference,
    )


def main():

    connection = (
        get_connection()
    )

    try:

        transactions = (
            load_transactions(
                connection
            )
        )

    finally:

        connection.close()

    (
        training_transactions,
        inference_transactions,
    ) = split_transactions(
        transactions
    )

    print(
        "\n"
        + "=" * 100
    )

    print(
        "DATASET SPLIT"
    )

    print(
        "=" * 100
    )

    print(
        f"All transactions: "
        f"{len(transactions)}"
    )

    print(
        f"Training transactions "
        f"(through June): "
        f"{len(training_transactions)}"
    )

    print(
        f"Inference transactions "
        f"(July/August): "
        f"{len(inference_transactions)}"
    )

    # ---------------------------------------------------------
    # FEATURE ENGINEERING
    # ---------------------------------------------------------

    engineer = (
        TransactionFeatureEngineer(
            home_country="India",

            related_party_names={
                "XYZ Holdings Pvt Ltd",
            },
        )
    )

    training_features = (
        engineer.fit_transform(
            training_transactions
        )
    )

    baseline = (
        engineer.get_baseline()
    )

    inference_features = (
        engineer.transform(
            inference_transactions,
            training=False,
        )
    )

    print(
        "\n"
        + "=" * 100
    )

    print(
        "HISTORICAL FEATURE BASELINE"
    )

    print(
        "=" * 100
    )

    print(
        f"Training transaction count: "
        f"{baseline.training_transaction_count}"
    )

    print(
        f"Historical median amount: "
        f"{baseline.median_amount}"
    )

    print(
        f"Historical total value: "
        f"{baseline.total_transaction_value}"
    )

    print(
        f"Last training timestamp: "
        f"{baseline.last_training_timestamp}"
    )

    print(
        f"Known historical counterparties: "
        f"{len(baseline.counterparty_frequency)}"
    )

    print(
        f"Feature version: "
        f"{baseline.feature_version}"
    )

    # ---------------------------------------------------------
    # ML TRAINING
    # ---------------------------------------------------------

    detector = (
        TransactionAnomalyDetector(
            contamination=0.05,
            n_estimators=200,
            random_state=42,
        )
    )

    detector.fit(
        training_features
    )

    # ---------------------------------------------------------
    # ML INFERENCE
    # ---------------------------------------------------------

    results = detector.score(
        inference_features
    )

    ranked_results = (
        detector.rank_by_anomaly(
            results
        )
    )

    anomalies = (
        detector.get_anomalies(
            results
        )
    )

    feature_lookup = {
        row["transaction_id"]: row
        for row in inference_features
    }

    # ---------------------------------------------------------
    # RESULTS
    # ---------------------------------------------------------

    print(
        "\n"
        + "=" * 100
    )

    print(
        "JULY / AUGUST INFERENCE RESULTS"
    )

    print(
        "=" * 100
    )

    for rank, result in enumerate(
        ranked_results,
        start=1,
    ):

        source = feature_lookup[
            result.transaction_id
        ]

        print(
            f"\nRank: {rank}"
        )

        print(
            f"Transaction: "
            f"{result.transaction_id}"
        )

        print(
            f"Date: "
            f"{source['transaction_timestamp']}"
        )

        print(
            f"Direction: "
            f"{source['direction']}"
        )

        print(
            f"Type: "
            f"{source['transaction_type']}"
        )

        print(
            f"Amount: "
            f"{source['amount']}"
        )

        print(
            f"Counterparty: "
            f"{source['counterparty_name']}"
        )

        print(
            f"Country: "
            f"{source['country']}"
        )

        print(
            f"Anomaly score: "
            f"{result.anomaly_score:.6f}"
        )

        print(
            f"Raw model score: "
            f"{result.raw_model_score:.6f}"
        )

        print(
            f"Prediction: "
            f"{result.model_prediction}"
        )

        print(
            f"Is anomaly: "
            f"{result.is_anomaly}"
        )

        print(
            "\nML features:"
        )

        for feature_name in (
            ML_FEATURES
        ):

            print(
                f"  {feature_name}: "
                f"{result.features[feature_name]:.4f}"
            )

        print(
            "\nRule context:"
        )

        print(
            "  related_party:",
            bool(
                source[
                    "is_related_party"
                ]
            ),
        )

        print(
            "  international:",
            bool(
                source[
                    "is_international"
                ]
            ),
        )

        print(
            "  round_amount:",
            bool(
                source[
                    "is_round_amount"
                ]
            ),
        )

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------

    print(
        "\n"
        + "=" * 100
    )

    print(
        "MODEL SUMMARY"
    )

    print(
        "=" * 100
    )

    print(
        f"Training transactions: "
        f"{detector.training_transaction_count}"
    )

    print(
        f"Inference transactions: "
        f"{len(results)}"
    )

    print(
        f"Inference anomalies: "
        f"{len(anomalies)}"
    )

    print(
        f"Training contamination: "
        f"{detector.contamination}"
    )

    print(
        f"Model version: "
        f"{results[0].model_version}"
    )

    print(
        f"Feature version: "
        f"{results[0].feature_version}"
    )


if __name__ == "__main__":
    main()