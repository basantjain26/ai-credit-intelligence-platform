import json

from src.transaction_investigation.tools import (
    TransactionInvestigationContext,
    TransactionInvestigationTools,
)


customer_id = "CUST_000001"
application_id = "APP_2026_00001"


def print_result(
    title: str,
    result: dict,
) -> None:

    print(
        "\n"
        + "=" * 100
    )

    print(
        title
    )

    print(
        "=" * 100
    )

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        )
    )


def main():

    print(
        "\nBuilding transaction "
        "investigation context..."
    )

    context = (
        TransactionInvestigationContext.build(
            customer_id=customer_id,
            application_id=application_id,
            contamination=0.05,
        )
    )

    print(
        "Context built successfully."
    )

    print(
        f"Training transactions: "
        f"{len(context.training_transactions)}"
    )

    print(
        f"Inference transactions: "
        f"{len(context.inference_transactions)}"
    )

    print(
        f"Model version: "
        f"{context.model_version}"
    )

    print(
        f"Feature version: "
        f"{context.feature_baseline.feature_version}"
    )

    tools = (
        TransactionInvestigationTools(
            context=context
        )
    )

    # =========================================================
    # TOOL 1
    # =========================================================

    summary = (
        tools.get_transaction_summary()
    )

    print_result(
        "TOOL 1 — TRANSACTION SUMMARY",
        summary,
    )

    # =========================================================
    # TOOL 2
    # =========================================================

    anomalies = (
        tools.get_anomalous_transactions(
            limit=10
        )
    )

    print_result(
        "TOOL 2 — ANOMALOUS TRANSACTIONS",
        anomalies,
    )

    # =========================================================
    # TOOL 3A
    # Known related party
    # =========================================================

    xyz_context = (
        tools.get_counterparty_context(
            counterparty_name=(
                "XYZ Holdings Pvt Ltd"
            )
        )
    )

    print_result(
        "TOOL 3 — XYZ HOLDINGS CONTEXT",
        xyz_context,
    )

    # =========================================================
    # TOOL 3B
    # International counterparty
    # =========================================================

    orion_context = (
        tools.get_counterparty_context(
            counterparty_name=(
                "Orion Global Trading LLC"
            )
        )
    )

    print_result(
        "TOOL 3 — ORION CONTEXT",
        orion_context,
    )


if __name__ == "__main__":
    main()