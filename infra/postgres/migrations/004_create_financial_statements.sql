CREATE TABLE financial_statements (
    statement_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    fiscal_year INTEGER NOT NULL,

    revenue NUMERIC(18,2),
    cogs NUMERIC(18,2),
    gross_profit NUMERIC(18,2),
    ebitda NUMERIC(18,2),
    operating_income NUMERIC(18,2),
    net_income NUMERIC(18,2),

    cash NUMERIC(18,2),
    accounts_receivable NUMERIC(18,2),
    inventory NUMERIC(18,2),
    current_assets NUMERIC(18,2),
    total_assets NUMERIC(18,2),

    accounts_payable NUMERIC(18,2),
    current_liabilities NUMERIC(18,2),
    short_term_debt NUMERIC(18,2),
    long_term_debt NUMERIC(18,2),
    total_debt NUMERIC(18,2),

    shareholder_equity NUMERIC(18,2),
    operating_cash_flow NUMERIC(18,2),
    capital_expenditure NUMERIC(18,2),
    interest_expense NUMERIC(18,2),

    source_document_id VARCHAR(50),
    audit_status VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_financial_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),

    CONSTRAINT uq_customer_fiscal_year
        UNIQUE (customer_id, fiscal_year)
);