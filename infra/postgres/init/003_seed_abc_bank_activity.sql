INSERT INTO bank_accounts (
    account_id,
    customer_id,
    account_type,
    currency,
    open_date,
    current_balance,
    average_monthly_balance,
    account_status
)
VALUES
(
    'ACC_001',
    'CUST_000001',
    'CURRENT_ACCOUNT',
    'INR',
    '2019-06-01',
    28500000.00,
    22000000.00,
    'ACTIVE'
),
(
    'ACC_002',
    'CUST_000001',
    'WORKING_CAPITAL_ACCOUNT',
    'INR',
    '2023-07-01',
    8200000.00,
    10500000.00,
    'ACTIVE'
),
(
    'ACC_003',
    'CUST_000001',
    'PAYROLL_ACCOUNT',
    'INR',
    '2020-01-01',
    4800000.00,
    5500000.00,
    'ACTIVE'
);


INSERT INTO bank_transactions (
    transaction_id,
    account_id,
    customer_id,
    transaction_timestamp,
    direction,
    transaction_type,
    amount,
    currency,
    counterparty_name,
    counterparty_account,
    counterparty_bank,
    merchant_category,
    country,
    channel,
    description,
    balance_after_transaction
)
VALUES

-- Normal incoming customer payments
(
    'TXN_000001',
    'ACC_001',
    'CUST_000001',
    '2026-07-01 10:15:00',
    'CREDIT',
    'RTGS',
    12500000.00,
    'INR',
    'Global Auto Systems Ltd',
    'GA1002001',
    'HDFC Bank',
    'CUSTOMER_PAYMENT',
    'India',
    'ONLINE',
    'Invoice settlement INV-7842',
    34500000.00
),

(
    'TXN_000002',
    'ACC_001',
    'CUST_000001',
    '2026-07-03 11:30:00',
    'CREDIT',
    'NEFT',
    7800000.00,
    'INR',
    'Prime Motors Pvt Ltd',
    'PM2003455',
    'ICICI Bank',
    'CUSTOMER_PAYMENT',
    'India',
    'ONLINE',
    'Customer invoice payment',
    42300000.00
),

-- Normal supplier payment
(
    'TXN_000003',
    'ACC_001',
    'CUST_000001',
    '2026-07-05 14:05:00',
    'DEBIT',
    'RTGS',
    3200000.00,
    'INR',
    'Steel Supplies India Pvt Ltd',
    'SS400123',
    'Axis Bank',
    'SUPPLIER_PAYMENT',
    'India',
    'ONLINE',
    'Raw material payment',
    39100000.00
),

-- Normal utilities
(
    'TXN_000004',
    'ACC_001',
    'CUST_000001',
    '2026-07-07 09:20:00',
    'DEBIT',
    'NEFT',
    850000.00,
    'INR',
    'Maharashtra Industrial Power',
    'MIP001122',
    'State Bank of India',
    'UTILITY_PAYMENT',
    'India',
    'ONLINE',
    'Monthly industrial electricity bill',
    38250000.00
),

-- Payroll
(
    'TXN_000005',
    'ACC_003',
    'CUST_000001',
    '2026-07-31 16:30:00',
    'DEBIT',
    'TRANSFER',
    6200000.00,
    'INR',
    'ABC Manufacturing Payroll',
    NULL,
    NULL,
    'PAYROLL',
    'India',
    'BULK_TRANSFER',
    'Monthly employee payroll',
    5100000.00
),

-- Loan repayment
(
    'TXN_000006',
    'ACC_001',
    'CUST_000001',
    '2026-08-01 09:45:00',
    'DEBIT',
    'LOAN_PAYMENT',
    1150000.00,
    'INR',
    'Commercial Bank Loan Servicing',
    NULL,
    NULL,
    'LOAN_PAYMENT',
    'India',
    'AUTO_DEBIT',
    'Monthly term loan repayment',
    37100000.00
),

-- Normal supplier payment
(
    'TXN_000007',
    'ACC_001',
    'CUST_000001',
    '2026-08-03 12:10:00',
    'DEBIT',
    'RTGS',
    4700000.00,
    'INR',
    'Precision Components Ltd',
    'PC345901',
    'Kotak Mahindra Bank',
    'SUPPLIER_PAYMENT',
    'India',
    'ONLINE',
    'Component procurement',
    32400000.00
),

-- Suspicious related-party transaction
(
    'TXN_000008',
    'ACC_001',
    'CUST_000001',
    '2026-08-08 15:42:00',
    'DEBIT',
    'RTGS',
    37800000.00,
    'INR',
    'XYZ Holdings Pvt Ltd',
    'XYZ778899',
    'ICICI Bank',
    'CORPORATE_TRANSFER',
    'India',
    'ONLINE',
    'Strategic investment transfer',
    -5400000.00
),

-- Large round-number transfer
(
    'TXN_000009',
    'ACC_002',
    'CUST_000001',
    '2026-08-10 10:05:00',
    'DEBIT',
    'RTGS',
    10000000.00,
    'INR',
    'Nova Industrial Traders',
    'NIT889900',
    'Axis Bank',
    'SUPPLIER_PAYMENT',
    'India',
    'ONLINE',
    'Advance payment',
    7200000.00
),

-- Another round-number transfer
(
    'TXN_000010',
    'ACC_002',
    'CUST_000001',
    '2026-08-10 10:22:00',
    'DEBIT',
    'RTGS',
    10000000.00,
    'INR',
    'Metro Commercial Ventures',
    'MCV220011',
    'HDFC Bank',
    'CORPORATE_TRANSFER',
    'India',
    'ONLINE',
    'Advance payment',
    -2800000.00
),

-- New counterparty, large payment
(
    'TXN_000011',
    'ACC_001',
    'CUST_000001',
    '2026-08-12 18:40:00',
    'DEBIT',
    'RTGS',
    16500000.00,
    'INR',
    'Orion Global Trading LLC',
    'OGT777331',
    'Emirates NBD',
    'INTERNATIONAL_TRADE',
    'UAE',
    'ONLINE',
    'Machinery procurement advance',
    -21900000.00
),

-- Later incoming customer payment
(
    'TXN_000012',
    'ACC_001',
    'CUST_000001',
    '2026-08-14 13:25:00',
    'CREDIT',
    'RTGS',
    24500000.00,
    'INR',
    'Global Auto Systems Ltd',
    'GA1002001',
    'HDFC Bank',
    'CUSTOMER_PAYMENT',
    'India',
    'ONLINE',
    'Invoice settlement INV-8129',
    2600000.00
);