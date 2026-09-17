from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


RANDOM_SEED = 42
NUMBER_OF_APPLICATIONS = 10_000

OUTPUT_PATH = Path(
    "data/ml/raw/historical_credit_applications.csv"
)


def sigmoid(value: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-value))


def generate_dataset() -> pd.DataFrame:
    rng = np.random.default_rng(RANDOM_SEED)

    company_age_years = np.clip(
        rng.normal(10, 6, NUMBER_OF_APPLICATIONS),
        1,
        40,
    )

    banking_relationship_years = np.clip(
        rng.normal(5, 4, NUMBER_OF_APPLICATIONS),
        0,
        25,
    )

    revenue = rng.lognormal(
        mean=np.log(500_000_000),
        sigma=0.8,
        size=NUMBER_OF_APPLICATIONS,
    )

    ebitda_margin = np.clip(
        rng.normal(0.14, 0.07, NUMBER_OF_APPLICATIONS),
        -0.10,
        0.40,
    )

    debt_to_ebitda = np.clip(
        rng.gamma(2.0, 1.2, NUMBER_OF_APPLICATIONS),
        0,
        10,
    )

    dscr = np.clip(
        rng.normal(1.55, 0.45, NUMBER_OF_APPLICATIONS),
        0.20,
        4.0,
    )

    current_ratio = np.clip(
        rng.normal(1.5, 0.45, NUMBER_OF_APPLICATIONS),
        0.30,
        4.0,
    )

    credit_score = np.clip(
        rng.normal(700, 70, NUMBER_OF_APPLICATIONS),
        400,
        850,
    )

    existing_exposure = rng.lognormal(
        mean=np.log(50_000_000),
        sigma=0.9,
        size=NUMBER_OF_APPLICATIONS,
    )

    past_due_count_12m = rng.poisson(
        0.6,
        NUMBER_OF_APPLICATIONS,
    )

    bureau_inquiries_6m = rng.poisson(
        1.5,
        NUMBER_OF_APPLICATIONS,
    )

    transaction_anomaly_rate = np.clip(
        rng.beta(2, 18, NUMBER_OF_APPLICATIONS),
        0,
        1,
    )

    related_party_transaction_ratio = np.clip(
        rng.beta(1.5, 15, NUMBER_OF_APPLICATIONS),
        0,
        1,
    )

    requested_amount = rng.lognormal(
        mean=np.log(40_000_000),
        sigma=0.8,
        size=NUMBER_OF_APPLICATIONS,
    )

    #
    # Hidden synthetic default mechanism.
    #
    # These coefficients create relationships between
    # borrower characteristics and future default risk.
    #
    risk_score = (
        -2.8
        + 1.20 * (1.25 - dscr)
        + 0.32 * (debt_to_ebitda - 2.0)
        + 0.75 * past_due_count_12m
        + 0.18 * bureau_inquiries_6m
        + 3.0 * transaction_anomaly_rate
        + 2.0 * related_party_transaction_ratio
        - 0.006 * (credit_score - 650)
        - 0.08 * banking_relationship_years
        - 0.50 * ebitda_margin
    )

    default_probability = sigmoid(risk_score)

    default_within_12m = rng.binomial(
        1,
        default_probability,
    )

    dataframe = pd.DataFrame(
        {
            "application_id": [
                f"HIST_APP_{index:06d}"
                for index in range(
                    1,
                    NUMBER_OF_APPLICATIONS + 1,
                )
            ],
            "company_age_years": company_age_years,
            "banking_relationship_years": (
                banking_relationship_years
            ),
            "revenue": revenue,
            "ebitda_margin": ebitda_margin,
            "debt_to_ebitda": debt_to_ebitda,
            "dscr": dscr,
            "current_ratio": current_ratio,
            "credit_score": credit_score,
            "existing_exposure": existing_exposure,
            "past_due_count_12m": past_due_count_12m,
            "bureau_inquiries_6m": bureau_inquiries_6m,
            "transaction_anomaly_rate": (
                transaction_anomaly_rate
            ),
            "related_party_transaction_ratio": (
                related_party_transaction_ratio
            ),
            "requested_amount": requested_amount,
            "default_within_12m": default_within_12m,
        }
    )

    return dataframe


def main() -> None:
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe = generate_dataset()

    dataframe.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    default_rate = (
        dataframe["default_within_12m"].mean()
    )

    print("=" * 70)
    print("CREDIT RISK TRAINING DATASET")
    print("=" * 70)

    print(
        f"Rows         : {len(dataframe):,}"
    )

    print(
        f"Features     : {len(dataframe.columns) - 2}"
    )

    print(
        f"Defaults     : "
        f"{dataframe['default_within_12m'].sum():,}"
    )

    print(
        f"Default rate : {default_rate:.2%}"
    )

    print(
        f"Output       : {OUTPUT_PATH}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()