from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class DataQualitySeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass
class DataQualityIssue:
    """
    One deterministic data-quality limitation affecting the
    reliability of financial analysis.
    """

    issue_code: str

    severity: DataQualitySeverity

    title: str

    description: str

    source: str

    metadata: dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )


@dataclass
class FinancialConfidenceAssessment:
    """
    Deterministic assessment of how reliable the available
    financial-analysis inputs are.

    This is NOT credit risk.

    A financially weak borrower can have HIGH confidence if
    the underlying data is complete and reliable.
    """

    confidence_level: ConfidenceLevel

    confidence_score: int

    data_quality_issues: list[
        DataQualityIssue
    ]

    high_issue_count: int

    medium_issue_count: int

    low_issue_count: int

    successful_tool_count: int

    failed_tool_count: int

    verified_ratio_count: int

    verified_evidence_count: int

    summary: str


class FinancialConfidenceEngine:
    """
    Deterministically evaluate the quality and completeness of
    information used by the Financial Analysis Agent.

    The score starts at 100 and explicit penalties are applied
    for observable quality problems.

    The LLM does NOT determine this score.
    """

    STARTING_SCORE = 100

    HIGH_CONFIDENCE_MIN = 80
    MEDIUM_CONFIDENCE_MIN = 55

    PENALTIES = {
        "FINANCIAL_VALUE_CONFLICT": 15,
        "MISSING_FINANCIAL_VALUE": 8,
        "RATIO_NOT_CALCULABLE": 5,
        "INSUFFICIENT_TREND_HISTORY": 8,
        "FAILED_TOOL_EXECUTION": 12,
        "NO_DOCUMENT_EVIDENCE": 8,
        "FAILED_DOCUMENT_RETRIEVAL": 12,
        "NO_FINANCIAL_STATEMENTS": 25,
    }

    def assess(
        self,
        tool_executions: list[Any],
        provenance_validation: Any,
    ) -> FinancialConfidenceAssessment:

        issues: list[
            DataQualityIssue
        ] = []

        successful_tool_count = 0
        failed_tool_count = 0

        for execution in tool_executions:

            if getattr(
                execution,
                "success",
                False,
            ):
                successful_tool_count += 1

            else:
                failed_tool_count += 1

        self._check_financial_overview(
            tool_executions=tool_executions,
            issues=issues,
        )

        self._check_ratios(
            tool_executions=tool_executions,
            issues=issues,
        )

        self._check_trends(
            tool_executions=tool_executions,
            issues=issues,
        )

        self._check_tool_failures(
            tool_executions=tool_executions,
            issues=issues,
        )

        self._check_document_evidence(
            tool_executions=tool_executions,
            provenance_validation=(
                provenance_validation
            ),
            issues=issues,
        )

        issues = (
            self._deduplicate_issues(
                issues
            )
        )

        score = self._calculate_score(
            issues
        )

        confidence_level = (
            self._score_to_level(
                score
            )
        )

        high_count = sum(
            1
            for issue in issues
            if issue.severity
            == DataQualitySeverity.HIGH
        )

        medium_count = sum(
            1
            for issue in issues
            if issue.severity
            == DataQualitySeverity.MEDIUM
        )

        low_count = sum(
            1
            for issue in issues
            if issue.severity
            == DataQualitySeverity.LOW
        )

        verified_ratio_count = int(
            getattr(
                provenance_validation,
                "verified_ratio_count",
                0,
            )
            or 0
        )

        verified_evidence_count = int(
            getattr(
                provenance_validation,
                "verified_evidence_count",
                0,
            )
            or 0
        )

        return FinancialConfidenceAssessment(
            confidence_level=(
                confidence_level
            ),
            confidence_score=score,
            data_quality_issues=issues,
            high_issue_count=high_count,
            medium_issue_count=medium_count,
            low_issue_count=low_count,
            successful_tool_count=(
                successful_tool_count
            ),
            failed_tool_count=(
                failed_tool_count
            ),
            verified_ratio_count=(
                verified_ratio_count
            ),
            verified_evidence_count=(
                verified_evidence_count
            ),
            summary=self._build_summary(
                confidence_level=(
                    confidence_level
                ),
                score=score,
                issues=issues,
            ),
        )

    # ---------------------------------------------------------
    # RECONCILIATION / FINANCIAL DATA QUALITY
    # ---------------------------------------------------------

    def _check_financial_overview(
        self,
        tool_executions: list[Any],
        issues: list[
            DataQualityIssue
        ],
    ) -> None:

        executions = (
            self._successful_results(
                tool_executions,
                "get_financial_overview",
            )
        )

        if not executions:
            return

        # Use the latest successful call.
        result = executions[-1]

        statements = result.get(
            "financial_statements",
            [],
        )

        if not statements:

            issues.append(
                DataQualityIssue(
                    issue_code=(
                        "NO_FINANCIAL_STATEMENTS"
                    ),
                    severity=(
                        DataQualitySeverity.HIGH
                    ),
                    title=(
                        "No structured financial "
                        "statements available"
                    ),
                    description=(
                        "The financial overview did "
                        "not contain structured "
                        "financial statements."
                    ),
                    source=(
                        "get_financial_overview"
                    ),
                )
            )

        reconciled_metrics = result.get(
            "reconciled_metrics",
            [],
        )

        if not isinstance(
            reconciled_metrics,
            list,
        ):
            return

        for metric in (
            reconciled_metrics
        ):

            if not isinstance(
                metric,
                dict,
            ):
                continue

            status = self._enum_value(
                metric.get(
                    "status"
                )
            )

            metric_name = metric.get(
                "canonical_name"
            )

            fiscal_year = metric.get(
                "fiscal_year"
            )

            if status == "CONFLICT":

                issues.append(
                    DataQualityIssue(
                        issue_code=(
                            "FINANCIAL_VALUE_CONFLICT"
                        ),
                        severity=(
                            DataQualitySeverity.HIGH
                        ),
                        title=(
                            "Conflicting financial "
                            "values"
                        ),
                        description=(
                            f"{metric_name} for "
                            f"FY{fiscal_year} has "
                            "conflicting source values."
                        ),
                        source=(
                            "get_financial_overview"
                        ),
                        metadata={
                            "metric_name": (
                                metric_name
                            ),
                            "fiscal_year": (
                                fiscal_year
                            ),
                            "distinct_values": (
                                metric.get(
                                    "distinct_values"
                                )
                            ),
                        },
                    )
                )

            elif status == (
                "MISSING_VALUE"
            ):

                issues.append(
                    DataQualityIssue(
                        issue_code=(
                            "MISSING_FINANCIAL_VALUE"
                        ),
                        severity=(
                            DataQualitySeverity.MEDIUM
                        ),
                        title=(
                            "Missing financial value"
                        ),
                        description=(
                            f"{metric_name} for "
                            f"FY{fiscal_year} is "
                            "missing."
                        ),
                        source=(
                            "get_financial_overview"
                        ),
                        metadata={
                            "metric_name": (
                                metric_name
                            ),
                            "fiscal_year": (
                                fiscal_year
                            ),
                        },
                    )
                )

    # ---------------------------------------------------------
    # RATIO AVAILABILITY
    # ---------------------------------------------------------

    def _check_ratios(
        self,
        tool_executions: list[Any],
        issues: list[
            DataQualityIssue
        ],
    ) -> None:

        results = (
            self._successful_results(
                tool_executions,
                "get_financial_ratios",
            )
        )

        if not results:
            return

        ratios = results[-1].get(
            "ratios",
            [],
        )

        if not isinstance(
            ratios,
            list,
        ):
            return

        for ratio in ratios:

            if not isinstance(
                ratio,
                dict,
            ):
                continue

            status = self._enum_value(
                ratio.get(
                    "status"
                )
            )

            if status != (
                "NOT_CALCULABLE"
            ):
                continue

            ratio_name = ratio.get(
                "ratio_name"
            )

            fiscal_year = ratio.get(
                "fiscal_year"
            )

            reason = ratio.get(
                "reason"
            )

            issues.append(
                DataQualityIssue(
                    issue_code=(
                        "RATIO_NOT_CALCULABLE"
                    ),
                    severity=(
                        DataQualitySeverity.MEDIUM
                    ),
                    title=(
                        "Financial ratio unavailable"
                    ),
                    description=(
                        f"{ratio_name} for "
                        f"FY{fiscal_year} could not "
                        f"be calculated. "
                        f"Reason: {reason}"
                    ),
                    source=(
                        "get_financial_ratios"
                    ),
                    metadata={
                        "ratio_name": (
                            ratio_name
                        ),
                        "fiscal_year": (
                            fiscal_year
                        ),
                        "reason": reason,
                    },
                )
            )

    # ---------------------------------------------------------
    # TREND COMPLETENESS
    # ---------------------------------------------------------

    def _check_trends(
        self,
        tool_executions: list[Any],
        issues: list[
            DataQualityIssue
        ],
    ) -> None:

        results = (
            self._successful_results(
                tool_executions,
                "get_financial_trends",
            )
        )

        if not results:
            return

        result = results[-1]

        collections = [
            result.get(
                "metric_trends",
                [],
            ),
            result.get(
                "ratio_trends",
                [],
            ),
        ]

        for collection in collections:

            if not isinstance(
                collection,
                list,
            ):
                continue

            for trend in collection:

                if not isinstance(
                    trend,
                    dict,
                ):
                    continue

                status = self._enum_value(
                    trend.get(
                        "status"
                    )
                )

                if status != (
                    "NOT_CALCULABLE"
                ):
                    continue

                metric_name = (
                    trend.get(
                        "metric_name"
                    )
                )

                reason = trend.get(
                    "reason"
                )

                issues.append(
                    DataQualityIssue(
                        issue_code=(
                            "INSUFFICIENT_TREND_HISTORY"
                        ),
                        severity=(
                            DataQualitySeverity.MEDIUM
                        ),
                        title=(
                            "Insufficient trend history"
                        ),
                        description=(
                            f"Historical trend for "
                            f"{metric_name} could not "
                            f"be calculated. "
                            f"Reason: {reason}"
                        ),
                        source=(
                            "get_financial_trends"
                        ),
                        metadata={
                            "metric_name": (
                                metric_name
                            ),
                            "reason": reason,
                        },
                    )
                )

    # ---------------------------------------------------------
    # TOOL RELIABILITY
    # ---------------------------------------------------------

    def _check_tool_failures(
        self,
        tool_executions: list[Any],
        issues: list[
            DataQualityIssue
        ],
    ) -> None:

        for execution in (
            tool_executions
        ):

            if getattr(
                execution,
                "success",
                False,
            ):
                continue

            tool_name = getattr(
                execution,
                "tool_name",
                "UNKNOWN",
            )

            error = getattr(
                execution,
                "error",
                None,
            )

            if tool_name == (
                "search_financial_documents"
            ):

                issue_code = (
                    "FAILED_DOCUMENT_RETRIEVAL"
                )

                severity = (
                    DataQualitySeverity.HIGH
                )

                title = (
                    "Financial document "
                    "retrieval failed"
                )

            else:

                issue_code = (
                    "FAILED_TOOL_EXECUTION"
                )

                severity = (
                    DataQualitySeverity.HIGH
                )

                title = (
                    "Financial analysis "
                    "tool failed"
                )

            issues.append(
                DataQualityIssue(
                    issue_code=issue_code,
                    severity=severity,
                    title=title,
                    description=(
                        f"{tool_name} failed during "
                        f"financial investigation. "
                        f"Error: {error}"
                    ),
                    source=tool_name,
                    metadata={
                        "error": error,
                    },
                )
            )

    # ---------------------------------------------------------
    # DOCUMENT EVIDENCE QUALITY
    # ---------------------------------------------------------

    def _check_document_evidence(
        self,
        tool_executions: list[Any],
        provenance_validation: Any,
        issues: list[
            DataQualityIssue
        ],
    ) -> None:

        searches = [
            execution
            for execution
            in tool_executions
            if getattr(
                execution,
                "tool_name",
                None,
            )
            == "search_financial_documents"
        ]

        # The agent may legitimately not need document RAG.
        # Therefore absence of a search is NOT automatically
        # a quality problem.
        if not searches:
            return

        successful_searches = [
            execution
            for execution in searches
            if getattr(
                execution,
                "success",
                False,
            )
        ]

        if not successful_searches:
            # Failure already captured by _check_tool_failures.
            return

        total_results = 0

        for execution in (
            successful_searches
        ):

            result = getattr(
                execution,
                "result",
                {},
            )

            if not isinstance(
                result,
                dict,
            ):
                continue

            result_count = result.get(
                "result_count"
            )

            if isinstance(
                result_count,
                int,
            ):
                total_results += (
                    result_count
                )

            else:
                results = result.get(
                    "results",
                    [],
                )

                if isinstance(
                    results,
                    list,
                ):
                    total_results += len(
                        results
                    )

        if total_results == 0:

            issues.append(
                DataQualityIssue(
                    issue_code=(
                        "NO_DOCUMENT_EVIDENCE"
                    ),
                    severity=(
                        DataQualitySeverity.MEDIUM
                    ),
                    title=(
                        "No supporting document "
                        "evidence retrieved"
                    ),
                    description=(
                        "Financial document retrieval "
                        "was executed successfully but "
                        "returned no evidence."
                    ),
                    source=(
                        "search_financial_documents"
                    ),
                )
            )

            return

        verified_evidence_count = int(
            getattr(
                provenance_validation,
                "verified_evidence_count",
                0,
            )
            or 0
        )

        # This is informational rather than a penalty:
        # retrieved evidence may have been used for reasoning
        # without being attached to a final concern.
        if verified_evidence_count == 0:
            issues.append(
                DataQualityIssue(
                    issue_code=(
                        "NO_ATTACHED_DOCUMENT_EVIDENCE"
                    ),
                    severity=(
                        DataQualitySeverity.LOW
                    ),
                    title=(
                        "Retrieved evidence was not "
                        "attached to final findings"
                    ),
                    description=(
                        "Financial document evidence "
                        "was retrieved, but no final "
                        "strength, concern, or "
                        "inconsistency referenced it."
                    ),
                    source=(
                        "provenance_validation"
                    ),
                )
            )

    # ---------------------------------------------------------
    # SCORE
    # ---------------------------------------------------------

    def _calculate_score(
        self,
        issues: list[
            DataQualityIssue
        ],
    ) -> int:

        score = (
            self.STARTING_SCORE
        )

        for issue in issues:

            penalty = (
                self.PENALTIES.get(
                    issue.issue_code,
                    0,
                )
            )

            score -= penalty

        return max(
            0,
            min(
                100,
                score,
            ),
        )

    def _score_to_level(
        self,
        score: int,
    ) -> ConfidenceLevel:

        if score >= (
            self.HIGH_CONFIDENCE_MIN
        ):
            return (
                ConfidenceLevel.HIGH
            )

        if score >= (
            self.MEDIUM_CONFIDENCE_MIN
        ):
            return (
                ConfidenceLevel.MEDIUM
            )

        return ConfidenceLevel.LOW

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------

    @staticmethod
    def _build_summary(
        confidence_level: (
            ConfidenceLevel
        ),
        score: int,
        issues: list[
            DataQualityIssue
        ],
    ) -> str:

        if not issues:

            return (
                "Financial analysis confidence "
                f"is {confidence_level.value} "
                f"({score}/100). No material "
                "data-quality limitations were "
                "identified from the executed "
                "financial tools."
            )

        high_count = sum(
            1
            for issue in issues
            if issue.severity
            == DataQualitySeverity.HIGH
        )

        medium_count = sum(
            1
            for issue in issues
            if issue.severity
            == DataQualitySeverity.MEDIUM
        )

        low_count = sum(
            1
            for issue in issues
            if issue.severity
            == DataQualitySeverity.LOW
        )

        return (
            "Financial analysis confidence "
            f"is {confidence_level.value} "
            f"({score}/100), with "
            f"{high_count} high, "
            f"{medium_count} medium, and "
            f"{low_count} low data-quality "
            "issues identified."
        )

    # ---------------------------------------------------------
    # RESULT HELPERS
    # ---------------------------------------------------------

    @staticmethod
    def _successful_results(
        tool_executions: list[Any],
        tool_name: str,
    ) -> list[
        dict[
            str,
            Any,
        ]
    ]:

        results = []

        for execution in (
            tool_executions
        ):

            if getattr(
                execution,
                "tool_name",
                None,
            ) != tool_name:
                continue

            if not getattr(
                execution,
                "success",
                False,
            ):
                continue

            result = getattr(
                execution,
                "result",
                None,
            )

            if isinstance(
                result,
                dict,
            ):
                results.append(
                    result
                )

        return results

    # ---------------------------------------------------------
    # ISSUE DEDUPLICATION
    # ---------------------------------------------------------

    @staticmethod
    def _deduplicate_issues(
        issues: list[
            DataQualityIssue
        ],
    ) -> list[
        DataQualityIssue
    ]:

        unique: list[
            DataQualityIssue
        ] = []

        seen = set()

        for issue in issues:

            metadata_items = tuple(
                sorted(
                    (
                        str(key),
                        str(value),
                    )
                    for key, value
                    in issue.metadata.items()
                )
            )

            key = (
                issue.issue_code,
                issue.source,
                metadata_items,
            )

            if key in seen:
                continue

            seen.add(
                key
            )

            unique.append(
                issue
            )

        return unique

    # ---------------------------------------------------------
    # ENUM HELPER
    # ---------------------------------------------------------

    @staticmethod
    def _enum_value(
        value: Any,
    ) -> Any:

        if hasattr(
            value,
            "value",
        ):
            return value.value

        return value