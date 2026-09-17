from src.credit_risk.prediction_tool import (
    CreditRiskPredictionTool,
)


customer_id = "CUST_000001"
application_id = "APP_2026_00001"


def main() -> None:

    features = {
        "company_age_years": 12.0,
        "banking_relationship_years": 7.0,
        "revenue": 790_000_000.0,
        "ebitda_margin": 0.1203,
        "debt_to_ebitda": 1.3158,
        "dscr": 1.12,
        "current_ratio": 1.30,
        "credit_score": 680.0,
        "existing_exposure": 83_000_000.0,
        "past_due_count_12m": 2.0,
        "bureau_inquiries_6m": 3.0,
        "transaction_anomaly_rate": 0.08,
        "related_party_transaction_ratio": 0.10,
        "requested_amount": 50_000_000.0,
    }

    tool = CreditRiskPredictionTool()

    result = tool.predict(
        customer_id=customer_id,
        application_id=application_id,
        features=features,
    )

    print()
    print("=" * 70)
    print(
        "CREDIT RISK PD PREDICTION"
    )
    print("=" * 70)

    print()
    print(
        f"Customer ID    : "
        f"{result.customer_id}"
    )

    print(
        f"Application ID : "
        f"{result.application_id}"
    )

    print(
        f"PD             : "
        f"{result.probability_of_default:.4f}"
    )

    print(
        f"PD %           : "
        f"{result.probability_of_default * 100:.2f}%"
    )

    print(
        f"Model          : "
        f"{result.model_name}"
    )

    print(
        f"Model version  : "
        f"{result.model_version}"
    )

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
    