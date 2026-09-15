from src.financial_analysis.agent import (
    FinancialAnalysisAgent,
)


def main():

    customer_id = "CUST_000001"
    application_id = "APP_2026_00001"

    question = """
    Analyze the borrower's financial condition.

    Focus on:
    - profitability
    - leverage
    - liquidity
    - debt service capacity
    - historical financial deterioration
    - important inconsistencies

    Where useful, retrieve supporting evidence from the
    borrower's financial documents.

    Do not make a final approve/reject decision.
    """

    with FinancialAnalysisAgent(
        customer_id=customer_id,
        application_id=application_id,
        max_iterations=10,
    ) as agent:

        result = agent.run(
            question
        )

        print(
            "\n"
            + "=" * 80
        )

        print(
            "FINANCIAL ANALYSIS"
        )

        print(
            "=" * 80
        )

        print(
            result.analysis
        )

        print(
            "\n"
            + "=" * 80
        )

        print(
            "AGENT EXECUTION TRACE"
        )

        print(
            "=" * 80
        )

        print(
            "Iterations:",
            result.iterations,
        )

        print(
            "Tool calls:",
            len(
                result.tool_executions
            ),
        )

        for index, execution in enumerate(
            result.tool_executions,
            start=1,
        ):

            print(
                f"\nTool Call {index}"
            )

            print(
                "Tool:",
                execution.tool_name,
            )

            print(
                "Arguments:",
                execution.arguments,
            )

            print(
                "Success:",
                execution.success,
            )

            if execution.error:
                print(
                    "Error:",
                    execution.error,
                )


if __name__ == "__main__":
    main()