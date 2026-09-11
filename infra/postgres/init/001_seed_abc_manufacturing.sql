INSERT INTO customers (
    customer_id,
    legal_name,
    industry_code,
    industry_name,
    registration_number,
    incorporation_date,
    relationship_start_date,
    annual_turnover_band,
    employee_count,
    registered_city,
    registered_country,
    risk_classification,
    customer_status
)
VALUES (
    'CUST_000001',
    'ABC Manufacturing Pvt Ltd',
    'AUTO-COMP',
    'Auto Components Manufacturing',
    'CIN-ABC-2012-0001',
    '2012-04-15',
    '2019-06-01',
    'INR 500M-1000M',
    420,
    'Pune',
    'India',
    'MEDIUM',
    'ACTIVE'
);

INSERT INTO company_directors (
    director_id,
    customer_id,
    director_name,
    ownership_percentage,
    role,
    appointment_date,
    active_flag
)
VALUES
(
    'DIR_001',
    'CUST_000001',
    'Rajesh Sharma',
    42.00,
    'Managing Director',
    '2012-04-15',
    TRUE
),
(
    'DIR_002',
    'CUST_000001',
    'Anita Sharma',
    28.00,
    'Director',
    '2012-04-15',
    TRUE
),
(
    'DIR_003',
    'CUST_000001',
    'Vikram Mehta',
    10.00,
    'Director',
    '2018-08-10',
    TRUE
);

INSERT INTO related_parties (
    related_party_id,
    customer_id,
    party_name,
    party_type,
    relationship_type,
    linked_director_id,
    registration_number,
    risk_level,
    effective_from
)
VALUES (
    'RP_001',
    'CUST_000001',
    'XYZ Holdings Pvt Ltd',
    'RELATED_COMPANY',
    'DIRECTOR_OWNED_ENTITY',
    'DIR_001',
    'CIN-XYZ-2018-0042',
    'HIGH',
    '2018-01-01'
);

INSERT INTO loan_applications (
    application_id,
    customer_id,
    application_date,
    loan_product,
    requested_amount,
    requested_term_months,
    loan_purpose,
    declared_revenue,
    declared_ebitda,
    declared_total_debt,
    requested_interest_rate,
    application_status
)
VALUES (
    'APP_2026_00001',
    'CUST_000001',
    '2026-08-15',
    'Working Capital Facility',
    50000000.00,
    36,
    'Working capital support for raw material procurement and operating expenses',
    850000000.00,
    105000000.00,
    83000000.00,
    10.250,
    'UNDER_REVIEW'
);