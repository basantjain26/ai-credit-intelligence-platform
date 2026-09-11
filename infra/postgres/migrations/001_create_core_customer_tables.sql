CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    legal_name VARCHAR(255) NOT NULL,
    industry_code VARCHAR(50),
    industry_name VARCHAR(255),
    registration_number VARCHAR(100) UNIQUE,
    incorporation_date DATE,
    relationship_start_date DATE,
    annual_turnover_band VARCHAR(100),
    employee_count INTEGER,
    registered_city VARCHAR(100),
    registered_country VARCHAR(100),
    risk_classification VARCHAR(50),
    customer_status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE company_directors (
    director_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    director_name VARCHAR(255) NOT NULL,
    ownership_percentage NUMERIC(5,2),
    role VARCHAR(100),
    appointment_date DATE,
    active_flag BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_director_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);

CREATE TABLE related_parties (
    related_party_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    party_name VARCHAR(255) NOT NULL,
    party_type VARCHAR(100),
    relationship_type VARCHAR(100),
    linked_director_id VARCHAR(50),
    registration_number VARCHAR(100),
    risk_level VARCHAR(50),
    effective_from DATE,
    effective_to DATE,

    CONSTRAINT fk_related_party_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),

    CONSTRAINT fk_related_party_director
        FOREIGN KEY (linked_director_id)
        REFERENCES company_directors(director_id)
);

CREATE TABLE loan_applications (
    application_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    application_date DATE NOT NULL,
    loan_product VARCHAR(100) NOT NULL,
    requested_amount NUMERIC(18,2) NOT NULL,
    requested_term_months INTEGER,
    loan_purpose TEXT,
    declared_revenue NUMERIC(18,2),
    declared_ebitda NUMERIC(18,2),
    declared_total_debt NUMERIC(18,2),
    requested_interest_rate NUMERIC(6,3),
    application_status VARCHAR(50) NOT NULL DEFAULT 'SUBMITTED',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_application_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);