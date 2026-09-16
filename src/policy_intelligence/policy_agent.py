from __future__ import annotations

import os

from openai import OpenAI
from pydantic import BaseModel, Field

from src.policy_intelligence.models import (
    PolicyEvaluationResult,
    PolicyFacts,
)

from src.policy_intelligence.policy_engine import (
    LendingPolicyEngine,
)

from src.rag.langchain_retriever import (
    CreditDocumentRetriever,
)


DEFAULT_MODEL = os.getenv(
    "OPENAI_AGENT_MODEL",
    "gpt-4.1-mini",
)


class PolicyFinding(BaseModel):
    policy_id: str

    status: str

    finding: str

    evidence_chunk_ids: list[str] = Field(
        default_factory=list
    )


class PolicyAgentResponse(BaseModel):
    summary: str

    findings: list[PolicyFinding]

    requires_credit_officer_review: bool

    review_reasons: list[str] = Field(
        default_factory=list
    )


class PolicyAgent:

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
    ) -> None:

        self.client = OpenAI()

        self.model = model

        self.policy_engine = (
            LendingPolicyEngine()
        )

        self.policy_retriever = (
            CreditDocumentRetriever(
                customer_id=None,
                application_id=None,
                document_type=(
                    "LENDING_POLICY"
                ),
                scope="ENTERPRISE",
                top_k=8,
            )
        )

    def evaluate(
        self,
        facts: PolicyFacts,
    ) -> PolicyAgentResponse:

        policy_result = (
            self.policy_engine.evaluate(
                facts
            )
        )

        policy_documents = (
            self._retrieve_policy_evidence(
                policy_result
            )
        )

        prompt = self._build_prompt(
            policy_result=policy_result,
            policy_documents=(
                policy_documents
            ),
        )

        response = (
            self.client.responses.parse(
                model=self.model,
                input=[
                    {
                        "role": "system",
                        "content": (
                            "You are a commercial "
                            "lending policy analysis "
                            "assistant. "
                            "You explain deterministic "
                            "policy evaluations using "
                            "retrieved policy evidence. "
                            "You must never change, "
                            "override, or recalculate "
                            "the supplied deterministic "
                            "policy statuses. "
                            "You must never independently "
                            "approve or reject a credit "
                            "application. "
                            "Only cite chunk IDs supplied "
                            "in the policy evidence."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                text_format=(
                    PolicyAgentResponse
                ),
            )
        )

        parsed = response.output_parsed

        if parsed is None:
            raise RuntimeError(
                "Policy Agent returned no "
                "structured response."
            )

        self._validate_response(
            agent_response=parsed,
            policy_result=policy_result,
            policy_documents=(
                policy_documents
            ),
        )

        return parsed

    def _retrieve_policy_evidence(
        self,
        policy_result: PolicyEvaluationResult,
    ) -> list:

        policy_ids = [
            evaluation.policy_id
            for evaluation
            in policy_result.evaluations
        ]

        query = (
            "Retrieve the commercial lending "
            "policy clauses for these policy "
            "rules: "
            + ", ".join(policy_ids)
            + ". Include DSCR, leverage, "
            "financial documentation, banking "
            "relationship, related-party "
            "transactions, unusual transactions, "
            "and credit decision authority."
        )

        return self.policy_retriever.invoke(
            query
        )

    @staticmethod
    def _build_prompt(
        policy_result: PolicyEvaluationResult,
        policy_documents: list,
    ) -> str:

        evaluation_lines = []

        for evaluation in (
            policy_result.evaluations
        ):

            evaluation_lines.append(
                "\n".join(
                    [
                        (
                            "Policy ID: "
                            f"{evaluation.policy_id}"
                        ),
                        (
                            "Status: "
                            f"{evaluation.status.value}"
                        ),
                        (
                            "Actual value: "
                            f"{evaluation.actual_value}"
                        ),
                        (
                            "Requirement: "
                            f"{evaluation.requirement}"
                        ),
                        (
                            "Deterministic reason: "
                            f"{evaluation.reason}"
                        ),
                    ]
                )
            )

        evidence_lines = []

        for document in policy_documents:

            chunk_id = (
                document.metadata.get(
                    "chunk_id"
                )
            )

            evidence_lines.append(
                "\n".join(
                    [
                        (
                            f"Chunk ID: "
                            f"{chunk_id}"
                        ),
                        (
                            "Policy text:"
                        ),
                        document.page_content,
                    ]
                )
            )

        return (
            "DETERMINISTIC POLICY RESULTS\n"
            "============================\n"
            + "\n\n".join(
                evaluation_lines
            )
            + "\n\n"
            + "RETRIEVED POLICY EVIDENCE\n"
            + "=========================\n"
            + "\n\n".join(
                evidence_lines
            )
            + "\n\n"
            + "TASK\n"
            + "====\n"
            + "Explain the policy assessment. "
            + "Preserve every deterministic "
            + "policy status exactly. "
            + "For each finding, cite only "
            + "relevant supplied chunk IDs. "
            + "If there is a VIOLATION, "
            + "ENHANCED_REVIEW, or "
            + "INSUFFICIENT_DATA status, "
            + "identify why human credit "
            + "officer review is required. "
            + "Do not approve or reject "
            + "the application."
        )

    @staticmethod
    def _validate_response(
        agent_response: PolicyAgentResponse,
        policy_result: PolicyEvaluationResult,
        policy_documents: list,
    ) -> None:

        expected_statuses = {
            evaluation.policy_id:
            evaluation.status.value
            for evaluation
            in policy_result.evaluations
        }

        valid_chunk_ids = {
            document.metadata.get(
                "chunk_id"
            )
            for document in policy_documents
            if document.metadata.get(
                "chunk_id"
            )
        }

        for finding in (
            agent_response.findings
        ):

            expected_status = (
                expected_statuses.get(
                    finding.policy_id
                )
            )

            if expected_status is None:
                raise ValueError(
                    "Policy Agent returned "
                    "an unknown policy ID: "
                    f"{finding.policy_id}"
                )

            if finding.status != (
                expected_status
            ):
                raise ValueError(
                    "Policy Agent attempted "
                    "to change deterministic "
                    "status for "
                    f"{finding.policy_id}. "
                    f"Expected "
                    f"{expected_status}, "
                    f"received "
                    f"{finding.status}."
                )

            for chunk_id in (
                finding.evidence_chunk_ids
            ):

                if chunk_id not in (
                    valid_chunk_ids
                ):
                    raise ValueError(
                        "Policy Agent cited "
                        "an unknown evidence "
                        "chunk: "
                        f"{chunk_id}"
                    )