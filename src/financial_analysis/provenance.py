from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from src.financial_analysis.schemas import (
    CalculatedRatioFinding,
    DocumentEvidenceReference,
    FinancialAnalysisOutput,
)


@dataclass
class ProvenanceValidationIssue:
    """
    One provenance validation failure.
    """

    issue_type: str
    location: str
    message: str


@dataclass
class ProvenanceValidationResult:
    """
    Result of validating an agent's final structured output
    against the actual tool executions from the same run.
    """

    valid: bool

    issues: list[
        ProvenanceValidationIssue
    ] = field(
        default_factory=list
    )

    verified_ratio_count: int = 0

    verified_evidence_count: int = 0


class FinancialProvenanceValidator:
    """
    Validate FinancialAnalysisOutput against actual tool
    executions.

    The validator does NOT trust the LLM's claims about:
    - ratio values
    - ratio status
    - ratio fiscal year
    - calculation formula
    - calculation inputs
    - document IDs
    - chunk IDs
    - document names
    - page numbers

    All such information must correspond to tool results
    observed during the current agent execution.
    """

    def validate(
        self,
        analysis: FinancialAnalysisOutput,
        tool_executions: list[Any],
    ) -> ProvenanceValidationResult:

        issues: list[
            ProvenanceValidationIssue
        ] = []

        ratio_registry = (
            self._build_ratio_registry(
                tool_executions
            )
        )

        evidence_registry = (
            self._build_evidence_registry(
                tool_executions
            )
        )

        verified_ratio_count = (
            self._validate_ratios(
                analysis=analysis,
                ratio_registry=ratio_registry,
                issues=issues,
            )
        )

        verified_evidence_count = (
            self._validate_all_evidence(
                analysis=analysis,
                evidence_registry=(
                    evidence_registry
                ),
                issues=issues,
            )
        )

        return ProvenanceValidationResult(
            valid=not issues,
            issues=issues,
            verified_ratio_count=(
                verified_ratio_count
            ),
            verified_evidence_count=(
                verified_evidence_count
            ),
        )

    # ---------------------------------------------------------
    # RATIO REGISTRY
    # ---------------------------------------------------------

    def _build_ratio_registry(
        self,
        tool_executions: list[Any],
    ) -> dict[
        tuple[str, int | None],
        dict[str, Any],
    ]:
        """
        Build a lookup of deterministic ratio results actually
        returned during this agent execution.

        Key:
            (ratio_name, fiscal_year)
        """

        registry: dict[
            tuple[str, int | None],
            dict[str, Any],
        ] = {}

        for execution in tool_executions:

            if not getattr(
                execution,
                "success",
                False,
            ):
                continue

            if getattr(
                execution,
                "tool_name",
                None,
            ) != "get_financial_ratios":
                continue

            result = getattr(
                execution,
                "result",
                None,
            )

            if not isinstance(
                result,
                dict,
            ):
                continue

            ratios = result.get(
                "ratios",
                []
            )

            if not isinstance(
                ratios,
                list,
            ):
                continue

            for ratio in ratios:

                if not isinstance(
                    ratio,
                    dict,
                ):
                    continue

                ratio_name = (
                    ratio.get(
                        "ratio_name"
                    )
                )

                fiscal_year = (
                    ratio.get(
                        "fiscal_year"
                    )
                )

                if not ratio_name:
                    continue

                registry[
                    (
                        str(ratio_name),
                        self._to_int(
                            fiscal_year
                        ),
                    )
                ] = ratio

        return registry

    # ---------------------------------------------------------
    # DOCUMENT EVIDENCE REGISTRY
    # ---------------------------------------------------------

    def _build_evidence_registry(
        self,
        tool_executions: list[Any],
    ) -> dict[str, dict[str, Any]]:
        """
        Build a registry of document chunks actually returned
        by search_financial_documents during this agent run.

        chunk_id is used as the primary evidence identifier.
        """

        registry: dict[
            str,
            dict[str, Any],
        ] = {}

        for execution in tool_executions:

            if not getattr(
                execution,
                "success",
                False,
            ):
                continue

            if getattr(
                execution,
                "tool_name",
                None,
            ) != (
                "search_financial_documents"
            ):
                continue

            result = getattr(
                execution,
                "result",
                None,
            )

            if not isinstance(
                result,
                dict,
            ):
                continue

            evidence_results = (
                result.get(
                    "results",
                    []
                )
            )

            if not isinstance(
                evidence_results,
                list,
            ):
                continue

            for evidence in (
                evidence_results
            ):

                if not isinstance(
                    evidence,
                    dict,
                ):
                    continue

                chunk_id = (
                    evidence.get(
                        "chunk_id"
                    )
                )

                if not chunk_id:
                    continue

                registry[
                    str(chunk_id)
                ] = evidence

        return registry

    # ---------------------------------------------------------
    # RATIO VALIDATION
    # ---------------------------------------------------------

    def _validate_ratios(
        self,
        analysis: FinancialAnalysisOutput,
        ratio_registry: dict[
            tuple[str, int | None],
            dict[str, Any],
        ],
        issues: list[
            ProvenanceValidationIssue
        ],
    ) -> int:

        verified_count = 0

        for index, finding in enumerate(
            analysis.calculated_ratios
        ):

            location = (
                f"calculated_ratios[{index}]"
            )

            key = (
                finding.ratio_name,
                finding.fiscal_year,
            )

            tool_ratio = (
                ratio_registry.get(
                    key
                )
            )

            if tool_ratio is None:

                issues.append(
                    ProvenanceValidationIssue(
                        issue_type=(
                            "UNVERIFIED_RATIO"
                        ),
                        location=location,
                        message=(
                            "Ratio was not returned by "
                            "get_financial_ratios during "
                            "this agent execution: "
                            f"{finding.ratio_name}, "
                            f"FY{finding.fiscal_year}"
                        ),
                    )
                )

                continue

            ratio_valid = True

            # -------------------------------------------------
            # Status
            # -------------------------------------------------

            tool_status = (
                self._enum_value(
                    tool_ratio.get(
                        "status"
                    )
                )
            )

            if finding.status != tool_status:

                ratio_valid = False

                issues.append(
                    ProvenanceValidationIssue(
                        issue_type=(
                            "RATIO_STATUS_MISMATCH"
                        ),
                        location=location,
                        message=(
                            "Agent ratio status does not "
                            "match deterministic tool "
                            f"result. Agent="
                            f"{finding.status}, "
                            f"Tool={tool_status}"
                        ),
                    )
                )

            # -------------------------------------------------
            # Value
            # -------------------------------------------------

            if not self._numeric_equal(
                finding.value,
                tool_ratio.get(
                    "value"
                ),
            ):

                ratio_valid = False

                issues.append(
                    ProvenanceValidationIssue(
                        issue_type=(
                            "RATIO_VALUE_MISMATCH"
                        ),
                        location=location,
                        message=(
                            "Agent ratio value does not "
                            "match deterministic tool "
                            f"result. Agent="
                            f"{finding.value}, "
                            f"Tool="
                            f"{tool_ratio.get('value')}"
                        ),
                    )
                )

            # -------------------------------------------------
            # Unit
            # -------------------------------------------------

            tool_unit = (
                tool_ratio.get(
                    "unit"
                )
            )

            if (
                finding.unit
                != tool_unit
            ):

                ratio_valid = False

                issues.append(
                    ProvenanceValidationIssue(
                        issue_type=(
                            "RATIO_UNIT_MISMATCH"
                        ),
                        location=location,
                        message=(
                            "Agent ratio unit does not "
                            "match deterministic tool "
                            f"result. Agent="
                            f"{finding.unit}, "
                            f"Tool={tool_unit}"
                        ),
                    )
                )

            # -------------------------------------------------
            # Calculation provenance
            # -------------------------------------------------

            provenance_valid = (
                self._validate_calculation_provenance(
                    finding=finding,
                    tool_ratio=tool_ratio,
                    location=location,
                    issues=issues,
                )
            )

            if not provenance_valid:
                ratio_valid = False

            if ratio_valid:
                verified_count += 1

        return verified_count

    def _validate_calculation_provenance(
        self,
        finding: CalculatedRatioFinding,
        tool_ratio: dict[str, Any],
        location: str,
        issues: list[
            ProvenanceValidationIssue
        ],
    ) -> bool:

        provenance = (
            finding.calculation_provenance
        )

        tool_formula = (
            tool_ratio.get(
                "formula"
            )
        )

        tool_inputs = (
            tool_ratio.get(
                "inputs",
                []
            )
        )

        # A ratio without provenance is not considered fully
        # verified when deterministic provenance exists.
        if provenance is None:

            if (
                tool_formula is not None
                or tool_inputs
            ):
                issues.append(
                    ProvenanceValidationIssue(
                        issue_type=(
                            "MISSING_CALCULATION_PROVENANCE"
                        ),
                        location=location,
                        message=(
                            "Agent omitted calculation "
                            "provenance available from "
                            "the deterministic ratio tool."
                        ),
                    )
                )

                return False

            return True

        valid = True

        if (
            provenance.formula
            != tool_formula
        ):

            valid = False

            issues.append(
                ProvenanceValidationIssue(
                    issue_type=(
                        "FORMULA_MISMATCH"
                    ),
                    location=location,
                    message=(
                        "Agent calculation formula "
                        "does not match deterministic "
                        f"tool formula. Agent="
                        f"{provenance.formula}, "
                        f"Tool={tool_formula}"
                    ),
                )
            )

        if not isinstance(
            tool_inputs,
            list,
        ):
            tool_inputs = []

        if (
            len(provenance.inputs)
            != len(tool_inputs)
        ):

            valid = False

            issues.append(
                ProvenanceValidationIssue(
                    issue_type=(
                        "CALCULATION_INPUT_COUNT_MISMATCH"
                    ),
                    location=location,
                    message=(
                        "Agent calculation input count "
                        "does not match deterministic "
                        "tool result."
                    ),
                )
            )

            return valid

        for input_index, (
            agent_input,
            tool_input,
        ) in enumerate(
            zip(
                provenance.inputs,
                tool_inputs,
            )
        ):

            input_location = (
                f"{location}."
                "calculation_provenance."
                f"inputs[{input_index}]"
            )

            if not isinstance(
                tool_input,
                dict,
            ):
                valid = False

                issues.append(
                    ProvenanceValidationIssue(
                        issue_type=(
                            "INVALID_TOOL_PROVENANCE"
                        ),
                        location=input_location,
                        message=(
                            "Deterministic tool returned "
                            "an invalid calculation input."
                        ),
                    )
                )

                continue

            if (
                agent_input.metric_name
                != tool_input.get(
                    "metric_name"
                )
            ):
                valid = False

                issues.append(
                    ProvenanceValidationIssue(
                        issue_type=(
                            "CALCULATION_INPUT_METRIC_MISMATCH"
                        ),
                        location=input_location,
                        message=(
                            "Calculation input metric "
                            "does not match tool result."
                        ),
                    )
                )

            if not self._numeric_equal(
                agent_input.value,
                tool_input.get(
                    "value"
                ),
            ):
                valid = False

                issues.append(
                    ProvenanceValidationIssue(
                        issue_type=(
                            "CALCULATION_INPUT_VALUE_MISMATCH"
                        ),
                        location=input_location,
                        message=(
                            "Calculation input value "
                            "does not match tool result."
                        ),
                    )
                )

            if (
                agent_input.fiscal_year
                != self._to_int(
                    tool_input.get(
                        "fiscal_year"
                    )
                )
            ):
                valid = False

                issues.append(
                    ProvenanceValidationIssue(
                        issue_type=(
                            "CALCULATION_INPUT_YEAR_MISMATCH"
                        ),
                        location=input_location,
                        message=(
                            "Calculation input fiscal "
                            "year does not match tool "
                            "result."
                        ),
                    )
                )

            tool_source_status = (
                self._enum_value(
                    tool_input.get(
                        "source_status"
                    )
                )
            )

            if (
                agent_input.source_status
                != tool_source_status
            ):
                valid = False

                issues.append(
                    ProvenanceValidationIssue(
                        issue_type=(
                            "CALCULATION_INPUT_SOURCE_MISMATCH"
                        ),
                        location=input_location,
                        message=(
                            "Calculation input source "
                            "status does not match tool "
                            "result."
                        ),
                    )
                )

        return valid

    # ---------------------------------------------------------
    # DOCUMENT EVIDENCE VALIDATION
    # ---------------------------------------------------------

    def _validate_all_evidence(
        self,
        analysis: FinancialAnalysisOutput,
        evidence_registry: dict[
            str,
            dict[str, Any],
        ],
        issues: list[
            ProvenanceValidationIssue
        ],
    ) -> int:

        verified_count = 0

        collections = [
            (
                "strengths",
                analysis.strengths,
            ),
            (
                "concerns",
                analysis.concerns,
            ),
            (
                "inconsistencies",
                analysis.inconsistencies,
            ),
        ]

        for (
            collection_name,
            collection,
        ) in collections:

            for item_index, item in enumerate(
                collection
            ):

                evidence_items = getattr(
                    item,
                    "evidence",
                    [],
                )

                for (
                    evidence_index,
                    evidence,
                ) in enumerate(
                    evidence_items
                ):

                    location = (
                        f"{collection_name}"
                        f"[{item_index}]"
                        f".evidence"
                        f"[{evidence_index}]"
                    )

                    if self._validate_evidence(
                        evidence=evidence,
                        evidence_registry=(
                            evidence_registry
                        ),
                        location=location,
                        issues=issues,
                    ):
                        verified_count += 1

        return verified_count

    def _validate_evidence(
        self,
        evidence: DocumentEvidenceReference,
        evidence_registry: dict[
            str,
            dict[str, Any],
        ],
        location: str,
        issues: list[
            ProvenanceValidationIssue
        ],
    ) -> bool:

        retrieved = (
            evidence_registry.get(
                evidence.chunk_id
            )
        )

        if retrieved is None:

            issues.append(
                ProvenanceValidationIssue(
                    issue_type=(
                        "UNKNOWN_EVIDENCE_ID"
                    ),
                    location=location,
                    message=(
                        "Agent referenced document "
                        "evidence that was not retrieved "
                        "during this execution. "
                        f"chunk_id="
                        f"{evidence.chunk_id}"
                    ),
                )
            )

            return False

        valid = True

        if (
            evidence.document_id
            != str(
                retrieved.get(
                    "document_id"
                )
            )
        ):

            valid = False

            issues.append(
                ProvenanceValidationIssue(
                    issue_type=(
                        "EVIDENCE_DOCUMENT_ID_MISMATCH"
                    ),
                    location=location,
                    message=(
                        "Evidence document_id does not "
                        "match retrieved evidence."
                    ),
                )
            )

        if (
            evidence.document_name
            != retrieved.get(
                "document_name"
            )
        ):

            valid = False

            issues.append(
                ProvenanceValidationIssue(
                    issue_type=(
                        "EVIDENCE_DOCUMENT_NAME_MISMATCH"
                    ),
                    location=location,
                    message=(
                        "Evidence document_name does "
                        "not match retrieved evidence."
                    ),
                )
            )

        if (
            evidence.page_number
            != self._to_int(
                retrieved.get(
                    "page_number"
                )
            )
        ):

            valid = False

            issues.append(
                ProvenanceValidationIssue(
                    issue_type=(
                        "EVIDENCE_PAGE_MISMATCH"
                    ),
                    location=location,
                    message=(
                        "Evidence page_number does not "
                        "match retrieved evidence."
                    ),
                )
            )

        return valid

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------

    @staticmethod
    def _numeric_equal(
        left: Any,
        right: Any,
    ) -> bool:
        """
        Compare numeric values without being sensitive to
        formatting differences such as:

            "1.1400"
            "1.14"

        None must match None.
        """

        if (
            left is None
            and right is None
        ):
            return True

        if (
            left is None
            or right is None
        ):
            return False

        try:
            return (
                Decimal(str(left))
                == Decimal(str(right))
            )

        except Exception:
            return (
                str(left)
                == str(right)
            )

    @staticmethod
    def _to_int(
        value: Any,
    ) -> int | None:

        if value is None:
            return None

        try:
            return int(value)

        except (
            TypeError,
            ValueError,
        ):
            return None

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