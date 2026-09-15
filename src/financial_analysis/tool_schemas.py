FINANCIAL_AGENT_TOOLS = [
    {
        "type": "function",
        "name": "get_financial_overview",
        "description": (
            "Get the borrower's available structured financial "
            "information and reconciled financial metrics. "
            "Use this when you need to understand what financial "
            "data is available or investigate conflicting or "
            "missing financial values."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "get_financial_ratios",
        "description": (
            "Get deterministically calculated financial ratios "
            "for the borrower across available fiscal years. "
            "Use this for leverage, profitability, liquidity, "
            "interest coverage, DSCR, and cash-flow ratios. "
            "Never calculate these ratios yourself."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "get_financial_trends",
        "description": (
            "Get deterministic historical financial trends, "
            "including revenue, EBITDA, net income, debt, "
            "operating cash flow, and financial-ratio movement. "
            "Use this when evaluating whether financial health "
            "is improving or deteriorating over time."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "get_financial_risk_signals",
        "description": (
            "Get deterministic financial risk signals generated "
            "from validated ratios and historical trends. "
            "These are financial-risk indicators and not final "
            "credit decisions or lending-policy violations."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "search_financial_documents",
        "description": (
            "Search borrower-scoped financial documents for "
            "supporting evidence. Use this when you need "
            "documentary support or context explaining a "
            "financial metric, trend, discrepancy, or risk "
            "signal. Results contain document and page "
            "provenance."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Specific semantic search query describing "
                        "the financial evidence needed."
                    ),
                },
                "limit": {
                    "type": "integer",
                    "description": (
                        "Maximum number of document chunks to "
                        "retrieve."
                    ),
                    "minimum": 1,
                    "maximum": 10,
                },
                "fiscal_year": {
                    "type": [
                        "integer",
                        "null",
                    ],
                    "description": (
                        "Optional fiscal year to restrict the "
                        "financial document search."
                    ),
                },
            },
            "required": [
                "query",
                "limit",
                "fiscal_year",
            ],
            "additionalProperties": False,
        },
    },
]