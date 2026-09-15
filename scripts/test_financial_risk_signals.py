from decimal import Decimal

from src.financial_analysis.ratio_engine import (
    FinancialRatioEngine,
)
from src.financial_analysis.reconciliation import (
    FinancialMetricObservation,
    FinancialValueReconciler,
)
from src.financial_analysis.risk_signals import (
    FinancialRiskSignalEngine,
)
from src.financial_analysis.trend_analysis import (
    HistoricalTrendAnalyzer,
)


def add_year(
    observations,
    fiscal_year,
    revenue,
    ebitda,
    net_income,
    debt,
    operating_cash_flow,
    equity,
    current_assets,
    current_liabilities,
    ebit,
    interest_expense,
    debt_service,
):

    values = {
        "revenue": revenue,
        "ebitda": ebitda,
        "net_income": net_income,
        "total_debt": debt,
        "operating_cash_flow": (
            operating_cash_flow
        ),
        "equity": equity,
        "current_assets": current_assets,
        "current_liabilities": (
            current_liabilities
        ),
        "ebit": ebit,
        "interest_expense": (
            interest_expense
        ),
        "debt_service": debt_service,
    }

    for metric_name, value in values.items():

        observations.append(
            FinancialMetricObservation(
                canonical_name=metric_name,
                value=Decimal(str(value)),
                source_type=(
                    "AUDITED_FINANCIAL_STATEMENT"
                ),
                fiscal_year=fiscal_year,
            )
        )


def main():

    observations = []

    add_year(
        observations=observations,
        fiscal_year=2025,
        revenue=860_000_000,
        ebitda=112_000_000,
        net_income=52_000_000,
        debt=100_000_000,
        operating_cash_flow=72_000_000,
        equity=200_000_000,
        current_assets=310_000_000,
        current_liabilities=170_000_000,
        ebit=94_000_000,
        interest_expense=15_000_000,
        debt_service=45_000_000,
    )

    add_year(
        observations=observations,
        fiscal_year=2026,
        revenue=790_000_000,
        ebitda=95_000_000,
        net_income=39_000_000,
        debt=125_000_000,
        operating_cash_flow=57_000_000,
        equity=210_000_000,
        current_assets=290_000_000,
        current_liabilities=180_000_000,
        ebit=78_000_000,
        interest_expense=18_000_000,
        debt_service=50_000_000,
    )

    reconciler = (
        FinancialValueReconciler()
    )

    reconciled = reconciler.reconcile(
        observations
    )

    ratio_engine = (
        FinancialRatioEngine()
    )

    ratios = ratio_engine.calculate_all(
        reconciled
    )

    trend_analyzer = (
        HistoricalTrendAnalyzer()
    )

    trend_analysis = (
        trend_analyzer.analyze(
            metrics=reconciled,
            ratios=ratios,
        )
    )

    signal_engine = (
        FinancialRiskSignalEngine()
    )

    assessment = (
        signal_engine.evaluate(
            trend_analysis=trend_analysis,
            ratios=ratios,
        )
    )

    print(
        "\n========== FINANCIAL RISK SIGNALS ==========\n"
    )

    for signal in assessment.signals:

        print(
            f"Signal: {signal.signal_code}"
        )

        print(
            f"Category: "
            f"{signal.category.value}"
        )

        print(
            f"Severity: "
            f"{signal.severity.value}"
        )

        print(
            f"Title: {signal.title}"
        )

        print(
            f"Metric: "
            f"{signal.metric_name}"
        )

        print(
            f"Observed: "
            f"{signal.observed_value}"
        )

        print(
            f"Threshold: "
            f"{signal.threshold_value}"
        )

        print(
            f"Fiscal Year: "
            f"{signal.fiscal_year}"
        )

        print(
            f"Description: "
            f"{signal.description}"
        )

        print(
            f"Metadata: "
            f"{signal.metadata}"
        )

        print(
            "-" * 70
        )

    print(
        "\n========== SIGNAL SUMMARY ==========\n"
    )

    print(
        "HIGH:",
        assessment.high_count,
    )

    print(
        "MEDIUM:",
        assessment.medium_count,
    )

    print(
        "LOW:",
        assessment.low_count,
    )


if __name__ == "__main__":
    main()