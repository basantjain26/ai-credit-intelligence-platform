CREATE TABLE loans (
    loan_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    loan_product VARCHAR(100) NOT NULL,
    original_amount NUMERIC(18,2) NOT NULL,
    outstanding_balance NUMERIC(18,2) NOT NULL,
    interest_rate NUMERIC(6,3),
    origination_date DATE NOT NULL,
    maturity_date DATE,
    monthly_payment NUMERIC(18,2),
    loan_status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE',
    secured_flag BOOLEAN NOT NULL DEFAULT FALSE,
    collateral_id VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_loan_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);

CREATE TABLE loan_payments (
    payment_id VARCHAR(50) PRIMARY KEY,
    loan_id VARCHAR(50) NOT NULL,
    customer_id VARCHAR(50) NOT NULL,
    due_date DATE NOT NULL,
    payment_date DATE,
    amount_due NUMERIC(18,2) NOT NULL,
    amount_paid NUMERIC(18,2) DEFAULT 0,
    days_past_due INTEGER NOT NULL DEFAULT 0,
    payment_status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_payment_loan
        FOREIGN KEY (loan_id)
        REFERENCES loans(loan_id),

    CONSTRAINT fk_payment_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);