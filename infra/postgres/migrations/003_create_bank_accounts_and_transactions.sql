CREATE TABLE bank_accounts (
    account_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    account_type VARCHAR(100) NOT NULL,
    currency VARCHAR(10) NOT NULL DEFAULT 'INR',
    open_date DATE,
    current_balance NUMERIC(18,2),
    average_monthly_balance NUMERIC(18,2),
    account_status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_bank_account_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);

CREATE TABLE bank_transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    account_id VARCHAR(50) NOT NULL,
    customer_id VARCHAR(50) NOT NULL,
    transaction_timestamp TIMESTAMP NOT NULL,
    direction VARCHAR(10) NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    amount NUMERIC(18,2) NOT NULL,
    currency VARCHAR(10) NOT NULL DEFAULT 'INR',
    counterparty_name VARCHAR(255),
    counterparty_account VARCHAR(100),
    counterparty_bank VARCHAR(255),
    merchant_category VARCHAR(100),
    country VARCHAR(100),
    channel VARCHAR(50),
    description TEXT,
    balance_after_transaction NUMERIC(18,2),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_transaction_account
        FOREIGN KEY (account_id)
        REFERENCES bank_accounts(account_id),

    CONSTRAINT fk_transaction_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),

    CONSTRAINT chk_transaction_direction
        CHECK (direction IN ('CREDIT', 'DEBIT')),

    CONSTRAINT chk_transaction_amount
        CHECK (amount > 0)
);

CREATE INDEX idx_transactions_customer_time
    ON bank_transactions(customer_id, transaction_timestamp);

CREATE INDEX idx_transactions_account_time
    ON bank_transactions(account_id, transaction_timestamp);

CREATE INDEX idx_transactions_counterparty
    ON bank_transactions(counterparty_name);