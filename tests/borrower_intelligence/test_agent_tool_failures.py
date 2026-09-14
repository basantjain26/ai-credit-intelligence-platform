import json
from types import SimpleNamespace

import pytest

from src.borrower_intelligence.agent import (
    BorrowerIntelligenceAgent,
)


class FakeTools:
    def __init__(self):
        self.calls = []

    def execute(
        self,
        tool_name: str,
        arguments: dict | None = None,
    ):
        arguments = arguments or {}

        self.calls.append(
            {
                "tool_name": tool_name,
                "arguments": arguments,
            }
        )

        if tool_name == "get_borrower_signals":
            raise RuntimeError(
                "Database connection unavailable"
            )

        if tool_name == "get_borrower_profile":
            return {
                "customer_id": "CUST001",
                "customer_name": (
                    "ABC Manufacturing Pvt Ltd"
                ),
                "industry": "Manufacturing",
            }

        raise ValueError(
            f"Unexpected tool: {tool_name}"
        )

    def close(self):
        pass


class FakeResponsesAPI:
    def __init__(self):
        self.call_count = 0
        self.received_inputs = []

    def parse(
        self,
        *,
        model,
        instructions,
        input,
        tools,
        text_format,
    ):
        self.call_count += 1

        self.received_inputs.append(
            list(input)
        )

        if self.call_count == 1:
            return SimpleNamespace(
                id="resp-001",
                output=[
                    SimpleNamespace(
                        type="function_call",
                        name="get_borrower_signals",
                        arguments="{}",
                        call_id="call-001",
                    )
                ],
                output_parsed=None,
            )

        if self.call_count == 2:
            return SimpleNamespace(
                id="resp-002",
                output=[
                    SimpleNamespace(
                        type="function_call",
                        name="get_borrower_profile",
                        arguments="{}",
                        call_id="call-002",
                    )
                ],
                output_parsed=None,
            )

        return SimpleNamespace(
            id="resp-003",
            output=[],
            output_parsed=text_format(
                borrower_summary=(
                    "ABC Manufacturing Pvt Ltd is "
                    "a manufacturing borrower."
                ),
                relationship_summary=(
                    "Relationship details are only "
                    "partially available."
                ),
                application_summary=(
                    "Application-level analysis is "
                    "limited because borrower signals "
                    "could not be retrieved."
                ),
                key_findings=[],
                inconsistencies=[],
                missing_information=[
                    (
                        "Deterministic borrower signals "
                        "could not be retrieved because "
                        "the database-dependent tool failed."
                    )
                ],
                investigation_items=[],
                overall_assessment=(
                    "Borrower profile information is "
                    "available, but the analysis is "
                    "incomplete because a required "
                    "structured-data dependency failed."
                ),
            ),
        )


class FakeClient:
    def __init__(self):
        self.responses = FakeResponsesAPI()


def build_agent():
    agent = (
        BorrowerIntelligenceAgent.__new__(
            BorrowerIntelligenceAgent
        )
    )

    agent.customer_id = "CUST001"
    agent.application_id = "APP001"
    agent.model = "fake-model"
    agent.max_iterations = 5

    agent.tools = FakeTools()
    agent.client = FakeClient()

    return agent


def test_tool_failure_does_not_crash_agent():

    agent = build_agent()

    result = agent.run(
        question=(
            "Analyze this borrower and identify "
            "important concerns."
        )
    )

    assert result is not None

    assert (
        result.output.borrower_summary
        == (
            "ABC Manufacturing Pvt Ltd is "
            "a manufacturing borrower."
        )
    )

    assert len(
        result.output.missing_information
    ) == 1

    assert (
        "could not be retrieved"
        in result.output.missing_information[0]
    )


def test_agent_continues_after_tool_failure():

    agent = build_agent()

    result = agent.run(
        question=(
            "Analyze this borrower."
        )
    )

    executed_tool_names = [
        execution.tool_name
        for execution
        in result.tool_executions
    ]

    assert (
        "get_borrower_profile"
        in executed_tool_names
    )


def test_failed_tool_is_returned_to_model_as_error():

    agent = build_agent()

    agent.run(
        question="Analyze this borrower."
    )

    second_request_input = (
        agent.client.responses
        .received_inputs[1]
    )

    function_outputs = [
        item
        for item
        in second_request_input
        if (
            isinstance(item, dict)
            and item.get("type")
            == "function_call_output"
        )
    ]

    assert len(function_outputs) == 1

    payload = json.loads(
        function_outputs[0]["output"]
    )

    assert (
        payload["status"]
        == "error"
    )

    assert (
        payload["error_type"]
        == "RuntimeError"
    )

    assert (
        "Database connection unavailable"
        in payload["message"]
    )


def test_successful_tool_after_failure_creates_evidence():

    agent = build_agent()

    result = agent.run(
        question="Analyze this borrower."
    )

    assert len(
        result.evidence
    ) == 1

    evidence = result.evidence[0]

    assert (
        evidence.evidence_id
        == "EVID-001"
    )

    assert (
        evidence.tool_name
        == "get_borrower_profile"
    )

    assert (
        evidence.source_type
        == "STRUCTURED_DATA"
    )


def test_failed_tool_does_not_create_false_evidence():

    agent = build_agent()

    result = agent.run(
        question="Analyze this borrower."
    )

    evidence_tool_names = {
        evidence.tool_name
        for evidence
        in result.evidence
    }

    assert (
        "get_borrower_signals"
        not in evidence_tool_names
    )