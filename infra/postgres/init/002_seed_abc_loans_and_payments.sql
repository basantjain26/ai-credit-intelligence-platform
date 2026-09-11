INSERT INTO loans (
    loan_id,
    customer_id,
    loan_product,
    original_amount,
    outstanding_balance,
    interest_rate,
    origination_date,
    maturity_date,
    monthly_payment,
    loan_status,
    secured_flag
)
VALUES
(
    'LOAN_001',
    'CUST_000001',
    'Term Loan',
    60000000.00,
    43000000.00,
    9.750,
    '2022-01-15',
    '2028-01-15',
    1150000.00,
    'ACTIVE',
    TRUE
),
(
    'LOAN_002',
    'CUST_000001',
    'Working Capital Facility',
    30000000.00,
    25000000.00,
    10.500,
    '2023-07-01',
    '2027-07-01',
    650000.00,
    'ACTIVE',
    FALSE
),
(
    'LOAN_003',
    'CUST_000001',
    'Equipment Finance',
    22000000.00,
    15000000.00,
    9.250,
    '2024-03-10',
    '2029-03-10',
    420000.00,
    'ACTIVE',
    TRUE
);

INSERT INTO loan_payments (
    payment_id,
    loan_id,
    customer_id,
    due_date,
    payment_date,
    amount_due,
    amount_paid,
    days_past_due,
    payment_status
)
VALUES
-- Mostly healthy behavior in 2024
('PAY_001', 'LOAN_001', 'CUST_000001', '2024-09-15', '2024-09-15', 1150000, 1150000, 0, 'ON_TIME'),
('PAY_002', 'LOAN_001', 'CUST_000001', '2024-10-15', '2024-10-15', 1150000, 1150000, 0, 'ON_TIME'),
('PAY_003', 'LOAN_001', 'CUST_000001', '2024-11-15', '2024-11-16', 1150000, 1150000, 1, 'LATE'),
('PAY_004', 'LOAN_001', 'CUST_000001', '2024-12-15', '2024-12-15', 1150000, 1150000, 0, 'ON_TIME'),

-- Mild deterioration in 2025
('PAY_005', 'LOAN_001', 'CUST_000001', '2025-01-15', '2025-01-18', 1150000, 1150000, 3, 'LATE'),
('PAY_006', 'LOAN_001', 'CUST_000001', '2025-02-15', '2025-02-20', 1150000, 1150000, 5, 'LATE'),
('PAY_007', 'LOAN_002', 'CUST_000001', '2025-03-01', '2025-03-01', 650000, 650000, 0, 'ON_TIME'),
('PAY_008', 'LOAN_002', 'CUST_000001', '2025-04-01', '2025-04-08', 650000, 650000, 7, 'LATE'),
('PAY_009', 'LOAN_003', 'CUST_000001', '2025-05-10', '2025-05-15', 420000, 420000, 5, 'LATE'),

-- Stronger deterioration in 2026
('PAY_010', 'LOAN_001', 'CUST_000001', '2026-01-15', '2026-01-30', 1150000, 1150000, 15, 'LATE'),
('PAY_011', 'LOAN_002', 'CUST_000001', '2026-02-01', '2026-02-20', 650000, 650000, 19, 'LATE'),
('PAY_012', 'LOAN_003', 'CUST_000001', '2026-03-10', '2026-04-02', 420000, 420000, 23, 'LATE'),
('PAY_013', 'LOAN_001', 'CUST_000001', '2026-04-15', '2026-05-15', 1150000, 1150000, 30, 'LATE'),
('PAY_014', 'LOAN_002', 'CUST_000001', '2026-05-01', NULL, 650000, 300000, 41, 'PARTIAL');