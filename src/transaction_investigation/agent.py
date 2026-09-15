from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from src.transaction_investigation.schemas import (
    TransactionInvestigationResult,
)
from src.transaction_investigation.tool_schemas import (
    TRANSACTION_TOOL_SCHEMAS,
)
from src.transaction_investigation.tools import (
    TransactionInvestigationContext,
    TransactionInvestigationTools,
)
from src.transaction_investigation.validator import (
    TransactionProvenanceValidator,
)


load_dotenv()


DEFAULT_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5.6",
)


SYSTEM_INSTRUCTIONS = """
You are a Transaction Investigation Agent supporting a commercial
bank credit analyst.

Your responsibility is to investigate the borrower's bank transaction
activity and identify patterns that may be relevant to credit risk.

You have trusted tools that provide:

1. deterministic transaction summaries,
2. Isolation Forest anomaly results,
3. counterparty and related-party context.

IMPORTANT RULES:

- Use tools to obtain transaction facts.

- Do not invent transaction amounts, transaction IDs, counterparties,
  anomaly scores, dates, countries, or related-party relationships.

- Do not treat an Isolation Forest anomaly as proof of fraud,
  misconduct, money laundering, or credit default.

- An Isolation Forest anomaly means the transaction is statistically
  unusual relative to the borrower's historical behavioral baseline.

- Distinguish between:
    * ML anomaly evidence,
    * deterministic business-rule evidence,
    * contextual interpretation.

- A transaction can be statistically unusual but legitimate.

- A transaction can be important because of a deterministic business
  rule even when the ML model does not classify it as an anomaly.

Pay particular attention to:

- unusually large transactions,
- new or rare counterparties,
- transaction velocity,
- related-party transfers,
- international transactions,
- unusual counterparty concentration,
- combinations of multiple risk indicators.

When an anomalous transaction involves a counterparty that appears
important, use the counterparty context tool when doing so would
materially improve the investigation.

Prefer evidence over speculation.

Clearly identify transaction IDs when discussing specific
transactions.

If available evidence is insufficient to determine why a transaction
occurred, state that additional analyst investigation or supporting
documentation is required.

Do not approve or reject the loan.

Do not claim that the borrower committed fraud.

The final structured output will be produced after the tool-based
investigation is complete.
""".strip()


class TransactionInvestigationAgent:
    """
    Transaction investigation agent using the OpenAI Responses API.

    High-level lifecycle:

        Build trusted investigation context
                    ↓
        Fit historical feature baseline
                    ↓
        Train Isolation Forest
                    ↓
        Score inference transactions
                    ↓
        LLM tool-calling investigation
                    ↓
        Structured Pydantic output

    No LangChain or LangGraph is used.
    """

    def __init__(
        self,
        customer_id: str,
        application_id: str,
        model: str = DEFAULT_MODEL,
        contamination: float = 0.05,
        max_tool_rounds: int = 10,
        log_tool_calls: bool = True,
    ) -> None:

        if not customer_id:
            raise ValueError(
                "customer_id is required"
            )

        if not application_id:
            raise ValueError(
                "application_id is required"
            )

        if max_tool_rounds < 1:
            raise ValueError(
                "max_tool_rounds must be at least 1"
            )

        self.customer_id = customer_id
        self.application_id = application_id

        self.model = model

        self.max_tool_rounds = (
            max_tool_rounds
        )

        self.log_tool_calls = (
            log_tool_calls
        )

        # =====================================================
        # BUILD TRUSTED INVESTIGATION CONTEXT ONCE
        #
        # This performs:
        #
        # - database loading
        # - training/inference split
        # - feature baseline fitting
        # - Isolation Forest training
        # - inference scoring
        # - related-party loading
        #
        # Agent tool calls reuse this prepared context.
        # =====================================================

        self.context = (
            TransactionInvestigationContext.build(
                customer_id=customer_id,
                application_id=application_id,
                contamination=contamination,
            )
        )

        self.tools = (
            TransactionInvestigationTools(
                context=self.context
            )
        )

        self.client = OpenAI()

    # =========================================================
    # PUBLIC API
    # =========================================================

    def investigate(
        self,
        question: str,
    ) -> TransactionInvestigationResult:
        """
        Run the complete transaction investigation.

        Phase 1:
            Agent dynamically selects and executes tools.

        Phase 2:
            Completed investigation is converted into the
            required Pydantic structured output.
        """

        if (
            not question
            or not question.strip()
        ):
            raise ValueError(
                "Investigation question "
                "cannot be empty."
            )

        # =====================================================
        # PHASE 1
        # AGENTIC TOOL-BASED INVESTIGATION
        # =====================================================

        response = (
            self.client.responses.create(
                model=self.model,
                instructions=(
                    SYSTEM_INSTRUCTIONS
                ),
                input=(
                    self._build_initial_prompt(
                        question
                    )
                ),
                tools=(
                    TRANSACTION_TOOL_SCHEMAS
                ),
            )
        )

        investigation_complete = False

        for tool_round in range(
            1,
            self.max_tool_rounds + 1,
        ):

            function_calls = [
                item
                for item in response.output
                if item.type
                == "function_call"
            ]

            # -------------------------------------------------
            # No function calls means the model believes it has
            # gathered enough evidence.
            # -------------------------------------------------

            if not function_calls:

                investigation_complete = (
                    True
                )

                break

            if self.log_tool_calls:

                print(
                    "\n"
                    + "-" * 100
                )

                print(
                    f"AGENT TOOL ROUND "
                    f"{tool_round}"
                )

                print(
                    "-" * 100
                )

            tool_outputs = []

            for function_call in (
                function_calls
            ):

                if self.log_tool_calls:

                    print(
                        "\n[AGENT TOOL CALL]"
                    )

                    print(
                        "Tool:",
                        function_call.name,
                    )

                    print(
                        "Arguments:",
                        function_call.arguments,
                    )

                # ---------------------------------------------
                # Execute only explicitly approved Python
                # capabilities.
                # ---------------------------------------------

                tool_result = (
                    self._execute_tool_call(
                        function_name=(
                            function_call.name
                        ),
                        arguments_json=(
                            function_call.arguments
                        ),
                    )
                )

                if self.log_tool_calls:

                    print(
                        "[TOOL COMPLETED]"
                    )

                # ---------------------------------------------
                # Return tool observation to the model.
                # ---------------------------------------------

                tool_outputs.append(
                    {
                        "type": (
                            "function_call_output"
                        ),

                        "call_id": (
                            function_call.call_id
                        ),

                        "output": (
                            json.dumps(
                                tool_result,
                                ensure_ascii=False,
                            )
                        ),
                    }
                )

            # -------------------------------------------------
            # Continue the SAME Responses API conversation.
            #
            # The model can now:
            #
            # - reason over the observations,
            # - call additional tools,
            # - or complete the investigation.
            # -------------------------------------------------

            response = (
                self.client.responses.create(
                    model=self.model,

                    instructions=(
                        SYSTEM_INSTRUCTIONS
                    ),

                    previous_response_id=(
                        response.id
                    ),

                    input=tool_outputs,

                    tools=(
                        TRANSACTION_TOOL_SCHEMAS
                    ),
                )
            )

        if not investigation_complete:

            # -------------------------------------------------
            # There is one subtle case:
            #
            # The final allowed tool round may itself produce
            # the final textual response.
            #
            # Check once before treating it as a loop failure.
            # -------------------------------------------------

            remaining_function_calls = [
                item
                for item in response.output
                if item.type
                == "function_call"
            ]

            if remaining_function_calls:

                raise RuntimeError(
                    "Transaction investigation "
                    "exceeded "
                    f"{self.max_tool_rounds} "
                    "tool rounds."
                )

            investigation_complete = True

        if not investigation_complete:

            raise RuntimeError(
                "Transaction investigation "
                "did not complete."
            )

        # =====================================================
        # PHASE 2
        # STRUCTURED OUTPUT
        # =====================================================

        if self.log_tool_calls:

            print(
                "\n"
                + "-" * 100
            )

            print(
                "GENERATING STRUCTURED "
                "INVESTIGATION RESULT"
            )

            print(
                "-" * 100
            )

        structured_response = (
            self.client.responses.parse(
                model=self.model,

                instructions=(
                    self
                    ._structured_output_instructions()
                ),

                previous_response_id=(
                    response.id
                ),

                input=(
                    "Using only the transaction "
                    "investigation and tool evidence "
                    "already gathered, produce the "
                    "final structured transaction "
                    "investigation."
                ),

                text_format=(
                    TransactionInvestigationResult
                ),
            )
        )

        result = (
            structured_response.output_parsed
        )

        if result is None:

            raise RuntimeError(
                "The model did not return "
                "a valid structured transaction "
                "investigation."
            )

        # =====================================================
        # TRUSTED CASE ID VALIDATION
        # =====================================================

        self._validate_result_scope(
            result
        )

        return result

    # =========================================================
    # TOOL DISPATCH
    # =========================================================

    def _execute_tool_call(
        self,
        function_name: str,
        arguments_json: str,
    ) -> dict[str, Any]:
        """
        Explicit allow-list dispatcher.

        The model is permitted to choose from approved tools,
        but it never receives arbitrary Python execution.
        """

        try:

            arguments = json.loads(
                arguments_json
                or "{}"
            )

        except json.JSONDecodeError as exc:

            raise RuntimeError(
                "Model returned invalid "
                "tool arguments for "
                f"{function_name}: "
                f"{arguments_json}"
            ) from exc

        # =====================================================
        # TOOL 1
        # =====================================================

        if (
            function_name
            == "get_transaction_summary"
        ):

            return (
                self.tools
                .get_transaction_summary()
            )

        # =====================================================
        # TOOL 2
        # =====================================================

        if (
            function_name
            == "get_anomalous_transactions"
        ):

            limit = arguments.get(
                "limit",
                10,
            )

            if not isinstance(
                limit,
                int,
            ):
                raise ValueError(
                    "limit must be an integer"
                )

            return (
                self.tools
                .get_anomalous_transactions(
                    limit=limit
                )
            )

        # =====================================================
        # TOOL 3
        # =====================================================

        if (
            function_name
            == "get_counterparty_context"
        ):

            counterparty_name = (
                arguments.get(
                    "counterparty_name"
                )
            )

            if (
                not counterparty_name
                or not isinstance(
                    counterparty_name,
                    str,
                )
            ):
                raise ValueError(
                    "counterparty_name "
                    "is required"
                )

            return (
                self.tools
                .get_counterparty_context(
                    counterparty_name=(
                        counterparty_name
                    )
                )
            )

        # =====================================================
        # SECURITY BOUNDARY
        # =====================================================

        raise ValueError(
            "Unsupported transaction tool: "
            f"{function_name}"
        )

    # =========================================================
    # INITIAL INVESTIGATION PROMPT
    # =========================================================

    def _build_initial_prompt(
        self,
        question: str,
    ) -> str:
        """
        Trusted customer/application identity is inserted by
        application code.

        It is NOT supplied as an LLM-controlled tool argument.
        """

        return f"""
Investigate transaction activity for the currently authorized
credit case.

TRUSTED CASE SCOPE

Customer ID:
{self.customer_id}

Application ID:
{self.application_id}

INVESTIGATION REQUEST

{question}

Use the available transaction investigation tools as needed.

Start by obtaining enough evidence to understand the borrower's
recent transaction behavior before reaching conclusions.

When important anomalous transactions involve counterparties whose
history or relationship matters, investigate those counterparties.

In your investigation:

- identify material transaction patterns,
- distinguish ML anomaly evidence from deterministic rule evidence,
- consider whether apparently unusual activity could have a legitimate
  explanation,
- identify relevant transaction IDs,
- identify issues requiring analyst follow-up,
- avoid unsupported conclusions,
- do not characterize anomalies as proven fraud,
- do not approve or reject the loan.

When you have gathered sufficient evidence, complete the investigation.
""".strip()

    # =========================================================
    # STRUCTURED OUTPUT INSTRUCTIONS
    # =========================================================

    def _structured_output_instructions(
        self,
    ) -> str:
        """
        Instructions used after the agent has completed its
        tool-based investigation.
        """

        return f"""
You are producing the final structured output from a completed
commercial-bank transaction investigation.

TRUSTED CASE IDENTITY

customer_id = {self.customer_id}

application_id = {self.application_id}

Use ONLY evidence already obtained during the transaction
investigation.

STRICT RULES

1. Never invent transaction IDs.

2. Never invent transaction amounts.

3. Never invent anomaly scores.

4. Never invent model versions.

5. Never invent feature versions.

6. Never invent related-party relationships.

7. Never invent countries or counterparties.

8. Isolation Forest anomalies represent statistical unusualness.
   They are NOT proof of fraud, misconduct, money laundering,
   or borrower default.

9. Clearly distinguish:
      - transaction evidence,
      - ML anomaly evidence,
      - deterministic business-rule evidence,
      - contextual interpretation.

10. A statistically unusual transaction may still be legitimate.

11. Include only material findings relevant to the credit
    investigation.

12. transaction_ids must contain the source transaction IDs
    supporting the finding.

13. When ML anomaly evidence is used and the tool evidence contains
    the anomaly score, model version, or feature version, preserve
    those values exactly.

14. analyst_follow_up should describe a concrete investigation
    action when further evidence is required.

15. If the business purpose of a transaction cannot be established
    from the available evidence, explicitly state that supporting
    documentation or analyst investigation is required.

16. Do not recommend automatic approval or rejection of the loan.

17. Use these trusted IDs exactly:

    customer_id = {self.customer_id}

    application_id = {self.application_id}

18. overall_transaction_risk represents the risk level arising from
    the transaction investigation only. It is NOT the borrower's
    final credit-risk rating or final lending decision.

19. Avoid duplicate findings. If multiple evidence items support the
    same underlying concern, combine them into one coherent finding
    when appropriate.

20. Add limitations where the available evidence does not establish
    transaction purpose, source of funds, beneficial ownership, or
    other facts necessary for a definitive conclusion.
""".strip()

    # =========================================================
    # TRUSTED RESULT VALIDATION
    # =========================================================

    def _validate_result_scope(
        self,
        result: TransactionInvestigationResult,
    ) -> None:
        """
        Pydantic validates structure.

        This additional deterministic check validates the trusted
        case identity.

        Full transaction/evidence provenance validation belongs
        to Step 5.4.
        """

        if (
            result.customer_id
            != self.customer_id
        ):

            raise RuntimeError(
                "Structured transaction "
                "investigation returned "
                "incorrect customer_id. "
                f"Expected "
                f"{self.customer_id}, "
                f"received "
                f"{result.customer_id}."
            )

        if (
            result.application_id
            != self.application_id
        ):

            raise RuntimeError(
                "Structured transaction "
                "investigation returned "
                "incorrect application_id. "
                f"Expected "
                f"{self.application_id}, "
                f"received "
                f"{result.application_id}."
            )