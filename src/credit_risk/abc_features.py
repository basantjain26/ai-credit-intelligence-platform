from __future__ import annotations


def build_abc_credit_risk_features() -> dict:

    revenue = 790_000_000.0
    ebitda = 95_000_000.0
    total_debt = 125_000_000.0

    ebitda_margin = (
        ebitda / revenue
    )

    debt_to_ebitda = (
        total_debt / ebitda
    )

    return {
        "company_age_years": None,

        "banking_relationship_years": 7.0,

        "revenue": revenue,

        "ebitda_margin": ebitda_margin,

        "debt_to_ebitda": debt_to_ebitda,

        "dscr": 1.12,

        "current_ratio": None,

        "credit_score": None,

        "existing_exposure": 83_000_000.0,

        "past_due_count_12m": None,

        "bureau_inquiries_6m": None,

        "transaction_anomaly_rate": None,

        "related_party_transaction_ratio": None,

        "requested_amount": 50_000_000.0,
    }