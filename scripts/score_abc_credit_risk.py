from src.credit_risk.abc_features import (
    build_abc_credit_risk_features,
)

from src.credit_risk.prediction_tool import (
    CreditRiskPredictionTool,
)


customer_id = "CUST_000001"
application_id = "APP_2026_00001"


def main() -> None:

    features = (
        build_abc_credit_risk_features()
    )

    tool = CreditRiskPredictionTool()

    prediction = tool.predict(
        customer_id=customer_id,
        application_id=application_id,
        features=features,
    )

    print()
    print("=" * 75)
    print(
        "ABC MANUFACTURING — "
        "CREDIT RISK MODEL"
    )
    print("=" * 75)

    print()
    print(
        f"Customer ID       : "
        f"{prediction.customer_id}"
    )

    print(
        f"Application ID    : "
        f"{prediction.application_id}"
    )

    print()
    print(
        f"Probability Default: "
        f"{prediction.probability_of_default:.4f}"
    )

    print(
        f"PD %               : "
        f"{prediction.probability_of_default * 100:.2f}%"
    )

    print()
    print(
        f"Model               : "
        f"{prediction.model_name}"
    )

    print(
        f"Model version       : "
        f"{prediction.model_version}"
    )

    print()
    print("MISSING / IMPUTED FEATURES")
    print("-" * 75)

    if prediction.missing_features:

        for feature in (
            prediction.missing_features
        ):
            print(
                f"- {feature}"
            )

    else:
        print("None")

    print()
    print("=" * 75)


if __name__ == "__main__":
    main()