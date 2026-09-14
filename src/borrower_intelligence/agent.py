import json
from dataclasses import dataclass, field
from typing import Any

from openai import OpenAI

from src.borrower_intelligence.evidence import (
    EvidenceRecord,
)
from src.borrower_intelligence.schemas import (
    BorrowerIntelligenceOutput,
)
from src.borrower_intelligence.tool_schemas import (
    BORROWER_TOOL_SCHEMAS,
)
from src.borrower_intelligence.tools import (
    BorrowerTools,
)
from src.settings import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
)


SYSTEM_INSTRUCTIONS = """
You are a Borrower Intelligence Agent supporting
commercial credit analysts.

Your responsibility is to understand the borrower
and identify borrower-level facts, inconsistencies,
missing information, and issues requiring further
investigation.

You have access to trusted tools containing:
- structured banking data,
- deterministic borrower signals,
- borrower document evidence.

IMPORTANT EVIDENCE RULES:

1. Tool results may contain evidence identifiers
   such as EVID-001, EVID-002, etc.

2. Every material key finding must reference the
   evidence IDs that support it.

3. Every inconsistency must reference the evidence
   IDs supporting the conflicting observations.

4. Every investigation item should reference
   supporting evidence IDs when evidence exists.

5. Never invent an evidence ID.

6. Only use evidence IDs explicitly returned by
   tools during this investigation.

7. If there is insufficient evidence for a claim,
   do not present the claim as a verified fact.

GENERAL RULES:

8. Use tools whenever borrower-specific facts are
   required.

9. Never invent borrower facts.

10. Never guess missing financial values.

11. Do not perform arithmetic yourself when a
    deterministic tool provides the calculation.

12. Prefer structured banking data for:
    - customer profile,
    - application data,
    - loans,
    - directors,
    - related parties,
    - exposure.

13. Use document search when documentary evidence
    is useful or the question concerns audited
    statements, borrower notes, reports, schedules,
    or other documents.

14. Clearly distinguish:
    - verified facts,
    - inconsistencies,
    - missing information,
    - investigation items.

15. If two sources disagree, report the discrepancy.
    Do not silently choose one value.

16. Do not approve or reject the credit application.

17. Do not make a final lending decision.

18. Severity must be one of:
    LOW, MEDIUM, HIGH.

19. Investigation priority must be one of:
    LOW, MEDIUM, HIGH.

20. Keep findings concise and useful to a
    commercial credit analyst.
"""


@dataclass
class ToolExecution:
    tool_name: str

    arguments: dict[str, Any]

    result: Any

    evidence_ids: list[str] = field(
        default_factory=list
    )


@dataclass
class BorrowerAgentResult:
    output: BorrowerIntelligenceOutput

    tool_executions: list[
        ToolExecution
    ] = field(
        default_factory=list
    )

    evidence: list[
        EvidenceRecord
    ] = field(
        default_factory=list
    )

    iterations: int = 0

    response_id: str | None = None


class BorrowerIntelligenceAgent:

    def __init__(
        self,
        customer_id: str,
        application_id: str,
        model: str | None = None,
        max_iterations: int = 8,
    ):
        self.customer_id = customer_id
        self.application_id = application_id

        self.model = (
            model
            or OPENAI_MODEL
        )

        self.max_iterations = (
            max_iterations
        )

        self.client = OpenAI(
            api_key=OPENAI_API_KEY
        )

        self.tools = BorrowerTools(
            customer_id=customer_id,
            application_id=application_id,
        )

    def run(
        self,
        question: str,
    ) -> BorrowerAgentResult:

        input_items: list[Any] = [
            {
                "role": "user",
                "content": question,
            }
        ]

        tool_executions: list[
            ToolExecution
        ] = []

        evidence_registry: list[
            EvidenceRecord
        ] = []

        for iteration in range(
            1,
            self.max_iterations + 1,
        ):

            response = (
                self.client.responses.parse(
                    model=self.model,
                    instructions=(
                        SYSTEM_INSTRUCTIONS
                    ),
                    input=input_items,
                    tools=(
                        BORROWER_TOOL_SCHEMAS
                    ),
                    text_format=(
                        BorrowerIntelligenceOutput
                    ),
                )
            )

            input_items.extend(
                response.output
            )

            function_calls = [
                item
                for item in response.output
                if item.type
                == "function_call"
            ]

            if not function_calls:

                parsed_output = (
                    response.output_parsed
                )

                if parsed_output is None:
                    raise RuntimeError(
                        "Model returned no "
                        "structured borrower "
                        "intelligence output."
                    )

                self._validate_evidence_references(
                    output=parsed_output,
                    evidence=(
                        evidence_registry
                    ),
                )

                return BorrowerAgentResult(
                    output=parsed_output,
                    tool_executions=(
                        tool_executions
                    ),
                    evidence=(
                        evidence_registry
                    ),
                    iterations=iteration,
                    response_id=response.id,
                )

            for function_call in (
                function_calls
            ):

                arguments = (
                    self._parse_arguments(
                        function_call.arguments
                    )
                )

                try:

                    result = (
                        self.tools.execute(
                            tool_name=(
                                function_call.name
                            ),
                            arguments=arguments,
                        )
                    )

                    (
                        evidence_records,
                        enriched_result,
                    ) = self._attach_evidence(
                        tool_name=(
                            function_call.name
                        ),
                        result=result,
                        evidence_registry=(
                            evidence_registry
                        ),
                    )

                    evidence_ids = [
                        record.evidence_id
                        for record
                        in evidence_records
                    ]

                    evidence_registry.extend(
                        evidence_records
                    )

                    tool_executions.append(
                        ToolExecution(
                            tool_name=(
                                function_call.name
                            ),
                            arguments=arguments,
                            result=result,
                            evidence_ids=(
                                evidence_ids
                            ),
                        )
                    )

                    tool_output = {
                        "status": "success",
                        "data": enriched_result,
                    }

                except Exception as exc:

                    tool_output = {
                        "status": "error",
                        "error_type": (
                            type(exc).__name__
                        ),
                        "message": str(exc),
                    }

                input_items.append(
                    {
                        "type": (
                            "function_call_output"
                        ),
                        "call_id": (
                            function_call.call_id
                        ),
                        "output": json.dumps(
                            tool_output,
                            default=str,
                        ),
                    }
                )

        raise RuntimeError(
            "Borrower agent exceeded "
            f"{self.max_iterations} "
            "tool-calling iterations."
        )

    def _attach_evidence(
        self,
        tool_name: str,
        result: Any,
        evidence_registry: list[
            EvidenceRecord
        ],
    ) -> tuple[
        list[EvidenceRecord],
        Any,
    ]:

        if (
            tool_name
            == "search_borrower_documents"
            and isinstance(result, list)
        ):
            return (
                self._attach_document_evidence(
                    tool_name=tool_name,
                    result=result,
                    existing_count=len(
                        evidence_registry
                    ),
                )
            )

        evidence_id = (
            self._next_evidence_id(
                len(evidence_registry)
            )
        )

        record = EvidenceRecord(
            evidence_id=evidence_id,
            source_type=(
                "STRUCTURED_DATA"
            ),
            source_name=tool_name,
            tool_name=tool_name,
            content=result,
        )

        enriched_result = {
            "evidence_id": evidence_id,
            "data": result,
        }

        return (
            [record],
            enriched_result,
        )

    def _attach_document_evidence(
        self,
        tool_name: str,
        result: list[dict[str, Any]],
        existing_count: int,
    ) -> tuple[
        list[EvidenceRecord],
        list[dict[str, Any]],
    ]:

        records: list[
            EvidenceRecord
        ] = []

        enriched_results: list[
            dict[str, Any]
        ] = []

        for offset, item in enumerate(
            result,
            start=1,
        ):

            evidence_id = (
                self._format_evidence_id(
                    existing_count
                    + offset
                )
            )

            record = EvidenceRecord(
                evidence_id=evidence_id,
                source_type="DOCUMENT",
                source_name=(
                    item.get(
                        "document_name"
                    )
                    or "unknown_document"
                ),
                tool_name=tool_name,
                document_id=(
                    item.get(
                        "document_id"
                    )
                ),
                document_name=(
                    item.get(
                        "document_name"
                    )
                ),
                page_number=(
                    item.get(
                        "page_number"
                    )
                ),
                content=(
                    item.get(
                        "chunk_text"
                    )
                ),
                metadata={
                    "chunk_id": (
                        item.get(
                            "chunk_id"
                        )
                    ),
                    "chunk_type": (
                        item.get(
                            "chunk_type"
                        )
                    ),
                    "similarity": (
                        item.get(
                            "similarity"
                        )
                    ),
                    "document_type": (
                        item.get(
                            "document_type"
                        )
                    ),
                },
            )

            records.append(
                record
            )

            enriched_item = dict(
                item
            )

            enriched_item[
                "evidence_id"
            ] = evidence_id

            enriched_results.append(
                enriched_item
            )

        return (
            records,
            enriched_results,
        )

    def _validate_evidence_references(
        self,
        output: BorrowerIntelligenceOutput,
        evidence: list[EvidenceRecord],
    ) -> None:

        valid_ids = {
            record.evidence_id
            for record in evidence
        }

        referenced_ids: set[str] = set()

        for finding in (
            output.key_findings
        ):
            referenced_ids.update(
                finding.evidence_ids
            )

        for inconsistency in (
            output.inconsistencies
        ):
            referenced_ids.update(
                inconsistency.evidence_ids
            )

        for item in (
            output.investigation_items
        ):
            referenced_ids.update(
                item.evidence_ids
            )

        invalid_ids = (
            referenced_ids
            - valid_ids
        )

        if invalid_ids:

            raise ValueError(
                "Agent referenced invalid "
                "evidence IDs: "
                + ", ".join(
                    sorted(
                        invalid_ids
                    )
                )
            )

    @staticmethod
    def _next_evidence_id(
        existing_count: int,
    ) -> str:

        return (
            BorrowerIntelligenceAgent
            ._format_evidence_id(
                existing_count + 1
            )
        )

    @staticmethod
    def _format_evidence_id(
        number: int,
    ) -> str:

        return (
            f"EVID-{number:03d}"
        )

    @staticmethod
    def _parse_arguments(
        raw_arguments: str,
    ) -> dict[str, Any]:

        if not raw_arguments:
            return {}

        arguments = json.loads(
            raw_arguments
        )

        if not isinstance(
            arguments,
            dict,
        ):
            raise ValueError(
                "Tool arguments must "
                "be a JSON object."
            )

        return arguments

    def close(
        self,
    ) -> None:

        self.tools.close()