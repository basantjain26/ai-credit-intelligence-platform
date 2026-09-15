TRANSACTION_TOOL_SCHEMAS = [
    {
        "type": "function",
        "name": "get_transaction_summary",
        "description": (
            "Get a deterministic summary of the borrower's "
            "transaction activity for the current investigation "
            "period, including debit/credit totals, largest "
            "transactions, related-party counts, international "
            "transaction counts, and ML anomaly count."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
        "strict": True,
    },

    {
        "type": "function",
        "name": "get_anomalous_transactions",
        "description": (
            "Get transactions classified as anomalies by the "
            "Isolation Forest behavioral anomaly model, ranked "
            "from most anomalous to least anomalous. Results "
            "include source transaction details, anomaly score, "
            "model lineage, feature values, and deterministic "
            "rule context."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 20,
                    "description": (
                        "Maximum number of anomalous "
                        "transactions to return."
                    ),
                }
            },
            "required": [
                "limit",
            ],
            "additionalProperties": False,
        },
        "strict": True,
    },

    {
        "type": "function",
        "name": "get_counterparty_context",
        "description": (
            "Investigate a specific transaction counterparty "
            "within the trusted borrower's transaction history. "
            "Returns historical relationship, transaction "
            "amounts, first/last seen dates, countries, anomaly "
            "results, and known related-party records."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "counterparty_name": {
                    "type": "string",
                    "description": (
                        "Exact counterparty name observed "
                        "in transaction evidence."
                    ),
                }
            },
            "required": [
                "counterparty_name",
            ],
            "additionalProperties": False,
        },
        "strict": True,
    },
]