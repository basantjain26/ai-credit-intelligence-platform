from pprint import pprint

from src.borrower_intelligence.agent import (
    BorrowerIntelligenceAgent,
)


def main():

    agent = BorrowerIntelligenceAgent(
        customer_id="CUST_000001",
        application_id="APP_2026_00001",
    )

    try:

        result = agent.run(
            question=(
                "Analyze this borrower and identify "
                "the most important borrower-level "
                "facts, inconsistencies, missing "
                "information, and issues that a "
                "credit analyst should investigate."
            )
        )

        output = result.output

        print(
            "\n========== BORROWER SUMMARY ==========\n"
        )

        print(
            output.borrower_summary
        )

        print(
            "\n========== RELATIONSHIP SUMMARY ==========\n"
        )

        print(
            output.relationship_summary
        )

        print(
            "\n========== APPLICATION SUMMARY ==========\n"
        )

        print(
            output.application_summary
        )

        print(
            "\n========== KEY FINDINGS ==========\n"
        )

        if not output.key_findings:
            print(
                "No key findings."
            )

        for finding in (
            output.key_findings
        ):

            print(
                f"[{finding.severity}] "
                f"{finding.title}"
            )

            print(
                finding.description
            )

            print(
                "Category:",
                finding.category,
            )

            print(
                "Evidence:",
                finding.evidence_ids,
            )

            print(
                "-" * 60
            )

        print(
            "\n========== INCONSISTENCIES ==========\n"
        )

        if not output.inconsistencies:
            print(
                "No inconsistencies identified."
            )

        for inconsistency in (
            output.inconsistencies
        ):

            print(
                inconsistency.title
            )

            print(
                inconsistency.description
            )

            print(
                "Source A:",
                inconsistency.source_a,
            )

            print(
                "Source B:",
                inconsistency.source_b,
            )

            print(
                "Requires follow-up:",
                inconsistency.requires_follow_up,
            )

            print(
                "Evidence:",
                inconsistency.evidence_ids,
            )

            print(
                "-" * 60
            )

        print(
            "\n========== MISSING INFORMATION ==========\n"
        )

        if not output.missing_information:
            print(
                "No missing information identified."
            )

        for item in (
            output.missing_information
        ):

            print(
                "-",
                item,
            )

        print(
            "\n========== INVESTIGATION ITEMS ==========\n"
        )

        if not output.investigation_items:
            print(
                "No investigation items identified."
            )

        for item in (
            output.investigation_items
        ):

            print(
                f"[{item.priority}] "
                f"{item.issue}"
            )

            print(
                item.reason
            )

            print(
                "Evidence:",
                item.evidence_ids,
            )

            print(
                "-" * 60
            )

        print(
            "\n========== OVERALL ASSESSMENT ==========\n"
        )

        print(
            output.overall_assessment
        )

        print(
            "\n========== TOOL EXECUTIONS ==========\n"
        )

        if not result.tool_executions:
            print(
                "No tools were executed."
            )

        for index, execution in enumerate(
            result.tool_executions,
            start=1,
        ):

            print(
                f"{index}. {execution.tool_name}"
            )

            print(
                "Arguments:"
            )

            pprint(
                execution.arguments
            )

            print(
                "Evidence IDs:"
            )

            pprint(
                execution.evidence_ids
            )

            print(
                "Result:"
            )

            pprint(
                execution.result
            )

            print(
                "-" * 60
            )

        print(
            "\n========== EVIDENCE REGISTRY ==========\n"
        )

        if not result.evidence:
            print(
                "No evidence records generated."
            )

        for evidence in (
            result.evidence
        ):

            print(
                evidence.evidence_id
            )

            print(
                "Source type:",
                evidence.source_type,
            )

            print(
                "Source name:",
                evidence.source_name,
            )

            print(
                "Tool:",
                evidence.tool_name,
            )

            if evidence.document_id:

                print(
                    "Document ID:",
                    evidence.document_id,
                )

            if evidence.document_name:

                print(
                    "Document:",
                    evidence.document_name,
                )

            if (
                evidence.page_number
                is not None
            ):

                print(
                    "Page:",
                    evidence.page_number,
                )

            if evidence.metadata:

                print(
                    "Metadata:"
                )

                pprint(
                    evidence.metadata
                )

            print(
                "Content:"
            )

            pprint(
                evidence.content
            )

            print(
                "-" * 60
            )

        print(
            "\n========== EXECUTION METADATA ==========\n"
        )

        print(
            "Iterations:",
            result.iterations,
        )

        print(
            "Response ID:",
            result.response_id,
        )

        print(
            "\n========== RAW STRUCTURED OUTPUT ==========\n"
        )

        pprint(
            output.model_dump()
        )

    finally:

        agent.close()


if __name__ == "__main__":
    main()