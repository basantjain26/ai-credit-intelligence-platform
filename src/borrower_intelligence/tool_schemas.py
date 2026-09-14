BORROWER_TOOL_SCHEMAS = [
    {
        "type": "function",
        "name": "get_borrower_profile",
        "description": (
            "Retrieve the current borrower's basic customer and company "
            "profile. Use this for company name, industry, relationship "
            "information, customer status, and other customer master "
            "attributes."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "get_application_details",
        "description": (
            "Retrieve details of the current credit application, including "
            "the requested facility, requested amount, purpose, application "
            "status, and information declared by the borrower."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "get_existing_exposure",
        "description": (
            "Retrieve the borrower's existing credit facilities and "
            "deterministic exposure calculations. Use this when you need "
            "existing outstanding exposure, requested amount, potential "
            "post-loan exposure, loan count, or existing loan details."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "get_directors",
        "description": (
            "Retrieve directors and management associated with the current "
            "borrower. Use this when investigating ownership, management, "
            "director information, or relationships involving directors."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "get_related_parties",
        "description": (
            "Retrieve entities and individuals identified as related parties "
            "of the current borrower, including available relationship, "
            "director linkage, and risk information. Use this when "
            "investigating related-party exposure or potentially concerning "
            "relationships."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "get_borrower_signals",
        "description": (
            "Retrieve deterministic borrower-level signals calculated by the "
            "application. These may include existing exposure, requested "
            "amount, potential post-loan exposure, relationship duration, "
            "director and related-party counts, high-risk related parties, "
            "declared versus audited revenue discrepancies, and missing "
            "information. Prefer this tool instead of performing arithmetic "
            "or deriving these signals yourself."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "search_borrower_documents",
        "description": (
            "Search indexed documents belonging to the current borrower or "
            "credit application using semantic similarity. Use this when "
            "documentary evidence is required from audited financial "
            "statements, borrower profiles, credit notes, exposure schedules, "
            "bureau reports, or other indexed borrower documents. The search "
            "is already restricted to the current borrower and application."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "A focused semantic search query describing the "
                        "specific borrower information or evidence needed. "
                        "For example: 'FY2026 audited revenue', "
                        "'management background', or "
                        "'existing credit facilities'."
                    ),
                },
                "limit": {
                    "type": "integer",
                    "description": (
                        "Maximum number of relevant document evidence chunks "
                        "to retrieve."
                    ),
                    "minimum": 1,
                    "maximum": 10,
                },
            },
            "required": [
                "query",
                "limit",
            ],
            "additionalProperties": False,
        },
    },
]