import os
import random
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

import psycopg2
from dotenv import load_dotenv


load_dotenv()


CUSTOMER_ID = "CUST_000001"

GENERATED_TRANSACTION_COUNT = 188

RANDOM_SEED = 42

START_DATE = datetime(
    2026,
    1,
    2,
    9,
    0,
)

END_DATE = datetime(
    2026,
    6,
    30,
    18,
    0,
)


CUSTOMER_RECEIPTS = [
    "Global Auto Systems Ltd",
    "Prime Motors Pvt Ltd",
    "Western Automotive Ltd",
    "National Vehicle Systems Ltd",
    "Pioneer Auto Components Ltd",
]

RAW_MATERIAL_SUPPLIERS = [
    "Steel Supplies India Pvt Ltd",
    "Bharat Alloy Traders",
    "Western Metals Pvt Ltd",
    "Industrial Steel Corporation",
    "Maharashtra Metal Works",
]

COMPONENT_SUPPLIERS = [
    "Precision Components Ltd",
    "Apex Industrial Components",
    "Reliable Bearings Pvt Ltd",
    "National Engineering Supplies",
]

LOGISTICS_PROVIDERS = [
    "FastTrack Logistics Pvt Ltd",
    "Western Freight Services",
    "National Transport Corporation",
]

UTILITY_PROVIDERS = [
    "Maharashtra Industrial Power",
    "Industrial Gas Services Ltd",
    "Maharashtra Water Services",
]

OTHER_OPERATING_COUNTERPARTIES = [
    "Industrial Estate Management",
    "Enterprise Software Solutions",
    "Factory Maintenance Services",
    "Industrial Safety Solutions",
]


def get_connection():
    """
    Connect using the same environment-driven approach as the
    rest of the project.

    Expected .env variables:

        POSTGRES_HOST
        POSTGRES_PORT
        POSTGRES_DB
        POSTGRES_USER
        POSTGRES_PASSWORD
    """

    return psycopg2.connect(
        host=os.getenv(
            "POSTGRES_HOST",
            "localhost",
        ),
        port=int(
            os.getenv(
                "POSTGRES_PORT",
                "5434",
            )
        ),
        dbname=os.getenv(
            "POSTGRES_DB",
            "credit_intelligence",
        ),
        user=os.getenv(
            "POSTGRES_USER",
            "credit_user",
        ),
        password=os.getenv(
            "POSTGRES_PASSWORD",
            "credit_password",
        ),
    )


def get_account_id(
    connection,
) -> str:
    """
    Resolve ABC Manufacturing's existing bank account.

    We deliberately reuse the account created in Step 1 rather
    than inventing another account ID.
    """

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT account_id
            FROM bank_accounts
            WHERE customer_id = %s
            ORDER BY account_id
            LIMIT 1
            """,
            (CUSTOMER_ID,),
        )

        row = cursor.fetchone()

    if not row:
        raise RuntimeError(
            f"No bank account found for "
            f"customer {CUSTOMER_ID}"
        )

    return row[0]


def random_business_timestamp(
    rng: random.Random,
) -> datetime:
    """
    Generate a timestamp primarily during normal business
    hours between January and June 2026.

    Existing July/August case transactions remain untouched.
    """

    total_days = (
        END_DATE.date()
        - START_DATE.date()
    ).days

    while True:
        day_offset = rng.randint(
            0,
            total_days,
        )

        candidate_date = (
            START_DATE
            + timedelta(
                days=day_offset
            )
        )

        # Primarily Monday-Friday.
        if candidate_date.weekday() >= 5:
            continue

        hour = rng.randint(
            9,
            17,
        )

        minute = rng.randint(
            0,
            59,
        )

        second = rng.randint(
            0,
            59,
        )

        return candidate_date.replace(
            hour=hour,
            minute=minute,
            second=second,
            microsecond=0,
        )


def money(
    rng: random.Random,
    minimum: int,
    maximum: int,
) -> Decimal:
    """
    Generate non-round operating amounts.

    We deliberately avoid making every normal transaction a
    perfect round number because round values are themselves a
    rule-oriented feature.
    """

    value = rng.uniform(
        minimum,
        maximum,
    )

    value += rng.uniform(
        100,
        95_000,
    )

    return Decimal(
        str(value)
    ).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )


def make_customer_receipt(
    rng: random.Random,
) -> dict:
    counterparty = rng.choice(
        CUSTOMER_RECEIPTS
    )

    return {
        "direction": "CREDIT",
        "transaction_type": rng.choice(
            [
                "RTGS",
                "NEFT",
            ]
        ),
        "amount": money(
            rng,
            2_000_000,
            14_000_000,
        ),
        "counterparty_name": counterparty,
        "counterparty_bank": rng.choice(
            [
                "HDFC Bank",
                "ICICI Bank",
                "State Bank of India",
                "Axis Bank",
            ]
        ),
        "merchant_category": (
            "CUSTOMER_RECEIPT"
        ),
        "country": "India",
        "channel": "CORPORATE_BANKING",
        "description": (
            f"Customer invoice receipt - "
            f"{counterparty}"
        ),
    }


def make_raw_material_payment(
    rng: random.Random,
) -> dict:
    counterparty = rng.choice(
        RAW_MATERIAL_SUPPLIERS
    )

    return {
        "direction": "DEBIT",
        "transaction_type": rng.choice(
            [
                "RTGS",
                "NEFT",
            ]
        ),
        "amount": money(
            rng,
            500_000,
            6_000_000,
        ),
        "counterparty_name": counterparty,
        "counterparty_bank": rng.choice(
            [
                "HDFC Bank",
                "ICICI Bank",
                "State Bank of India",
                "Bank of Baroda",
            ]
        ),
        "merchant_category": (
            "RAW_MATERIAL"
        ),
        "country": "India",
        "channel": "CORPORATE_BANKING",
        "description": (
            f"Raw material supplier payment - "
            f"{counterparty}"
        ),
    }


def make_component_payment(
    rng: random.Random,
) -> dict:
    counterparty = rng.choice(
        COMPONENT_SUPPLIERS
    )

    return {
        "direction": "DEBIT",
        "transaction_type": rng.choice(
            [
                "RTGS",
                "NEFT",
            ]
        ),
        "amount": money(
            rng,
            300_000,
            4_000_000,
        ),
        "counterparty_name": counterparty,
        "counterparty_bank": rng.choice(
            [
                "Axis Bank",
                "ICICI Bank",
                "State Bank of India",
            ]
        ),
        "merchant_category": (
            "COMPONENT_SUPPLIER"
        ),
        "country": "India",
        "channel": "CORPORATE_BANKING",
        "description": (
            f"Component supplier payment - "
            f"{counterparty}"
        ),
    }


def make_logistics_payment(
    rng: random.Random,
) -> dict:
    counterparty = rng.choice(
        LOGISTICS_PROVIDERS
    )

    return {
        "direction": "DEBIT",
        "transaction_type": "NEFT",
        "amount": money(
            rng,
            200_000,
            1_500_000,
        ),
        "counterparty_name": counterparty,
        "counterparty_bank": rng.choice(
            [
                "HDFC Bank",
                "Axis Bank",
            ]
        ),
        "merchant_category": "LOGISTICS",
        "country": "India",
        "channel": "CORPORATE_BANKING",
        "description": (
            f"Freight and logistics payment - "
            f"{counterparty}"
        ),
    }


def make_utility_payment(
    rng: random.Random,
) -> dict:
    counterparty = rng.choice(
        UTILITY_PROVIDERS
    )

    return {
        "direction": "DEBIT",
        "transaction_type": "NEFT",
        "amount": money(
            rng,
            500_000,
            1_200_000,
        ),
        "counterparty_name": counterparty,
        "counterparty_bank": (
            "State Bank of India"
        ),
        "merchant_category": "UTILITY",
        "country": "India",
        "channel": "CORPORATE_BANKING",
        "description": (
            f"Industrial utility payment - "
            f"{counterparty}"
        ),
    }


def make_operating_payment(
    rng: random.Random,
) -> dict:
    counterparty = rng.choice(
        OTHER_OPERATING_COUNTERPARTIES
    )

    return {
        "direction": "DEBIT",
        "transaction_type": "NEFT",
        "amount": money(
            rng,
            150_000,
            1_800_000,
        ),
        "counterparty_name": counterparty,
        "counterparty_bank": rng.choice(
            [
                "HDFC Bank",
                "ICICI Bank",
                "Axis Bank",
            ]
        ),
        "merchant_category": (
            "OPERATING_EXPENSE"
        ),
        "country": "India",
        "channel": "CORPORATE_BANKING",
        "description": (
            f"Operating expense payment - "
            f"{counterparty}"
        ),
    }


def make_payroll(
    rng: random.Random,
) -> dict:
    return {
        "direction": "DEBIT",
        "transaction_type": "TRANSFER",
        "amount": money(
            rng,
            5_200_000,
            6_800_000,
        ),
        "counterparty_name": (
            "ABC Manufacturing Payroll"
        ),
        "counterparty_bank": (
            "Commercial Bank"
        ),
        "merchant_category": "PAYROLL",
        "country": "India",
        "channel": "CORPORATE_BANKING",
        "description": (
            "Monthly employee payroll"
        ),
    }


def make_loan_payment(
    rng: random.Random,
) -> dict:
    return {
        "direction": "DEBIT",
        "transaction_type": (
            "LOAN_PAYMENT"
        ),
        "amount": money(
            rng,
            1_000_000,
            1_300_000,
        ),
        "counterparty_name": (
            "Commercial Bank Loan Servicing"
        ),
        "counterparty_bank": (
            "Commercial Bank"
        ),
        "merchant_category": (
            "DEBT_SERVICE"
        ),
        "country": "India",
        "channel": "INTERNAL_TRANSFER",
        "description": (
            "Scheduled commercial loan payment"
        ),
    }


def make_tax_payment(
    rng: random.Random,
) -> dict:
    return {
        "direction": "DEBIT",
        "transaction_type": "NEFT",
        "amount": money(
            rng,
            400_000,
            3_000_000,
        ),
        "counterparty_name": (
            "Government Tax Authority"
        ),
        "counterparty_bank": (
            "Reserve Bank Settlement"
        ),
        "merchant_category": "TAX",
        "country": "India",
        "channel": "CORPORATE_BANKING",
        "description": (
            "Statutory tax payment"
        ),
    }


def generate_transactions(
    account_id: str,
) -> list[dict]:
    """
    Generate exactly 188 reproducible normal-history
    transactions.

    random.Random with a fixed seed ensures rerunning the
    generator creates the same dataset.
    """

    rng = random.Random(
        RANDOM_SEED
    )

    generators = [
        # 45 customer receipts
        *(
            [make_customer_receipt]
            * 45
        ),

        # 45 raw-material supplier payments
        *(
            [make_raw_material_payment]
            * 45
        ),

        # 25 component supplier payments
        *(
            [make_component_payment]
            * 25
        ),

        # 18 logistics payments
        *(
            [make_logistics_payment]
            * 18
        ),

        # 12 utility payments
        *(
            [make_utility_payment]
            * 12
        ),

        # 15 other operating payments
        *(
            [make_operating_payment]
            * 15
        ),

        # 10 payroll-related transactions
        *(
            [make_payroll]
            * 10
        ),

        # 10 loan servicing transactions
        *(
            [make_loan_payment]
            * 10
        ),

        # 8 tax payments
        *(
            [make_tax_payment]
            * 8
        ),
    ]

    assert len(generators) == (
        GENERATED_TRANSACTION_COUNT
    )

    rng.shuffle(
        generators
    )

    transactions = []

    for index, generator in enumerate(
        generators,
        start=1,
    ):
        transaction = generator(
            rng
        )

        transaction[
            "transaction_id"
        ] = (
            f"TXN_HIST_{index:06d}"
        )

        transaction[
            "account_id"
        ] = account_id

        transaction[
            "customer_id"
        ] = CUSTOMER_ID

        transaction[
            "transaction_timestamp"
        ] = random_business_timestamp(
            rng
        )

        transaction[
            "currency"
        ] = "INR"

        transaction[
            "counterparty_account"
        ] = (
            f"CP{rng.randint(10000000, 99999999)}"
        )

        # Historical seed data does not attempt to reconstruct
        # a perfect running bank balance. We leave this null
        # rather than fabricating accounting lineage.
        transaction[
            "balance_after_transaction"
        ] = None

        transactions.append(
            transaction
        )

    transactions.sort(
        key=lambda row: (
            row["transaction_timestamp"],
            row["transaction_id"],
        )
    )

    return transactions


def insert_transactions(
    connection,
    transactions: list[dict],
) -> int:
    """
    Insert generated history.

    ON CONFLICT makes the script idempotent based on the
    bank_transactions primary key.
    """

    inserted_count = 0

    sql = """
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
        VALUES (
            %(transaction_id)s,
            %(account_id)s,
            %(customer_id)s,
            %(transaction_timestamp)s,
            %(direction)s,
            %(transaction_type)s,
            %(amount)s,
            %(currency)s,
            %(counterparty_name)s,
            %(counterparty_account)s,
            %(counterparty_bank)s,
            %(merchant_category)s,
            %(country)s,
            %(channel)s,
            %(description)s,
            %(balance_after_transaction)s
        )
        ON CONFLICT (transaction_id)
        DO NOTHING
        RETURNING transaction_id
    """

    with connection.cursor() as cursor:
        for transaction in transactions:
            cursor.execute(
                sql,
                transaction,
            )

            inserted = cursor.fetchone()

            if inserted:
                inserted_count += 1

    return inserted_count


def count_customer_transactions(
    connection,
) -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM bank_transactions
            WHERE customer_id = %s
            """,
            (CUSTOMER_ID,),
        )

        return cursor.fetchone()[0]


def main():
    connection = get_connection()

    try:
        account_id = get_account_id(
            connection
        )

        print(
            f"Customer: {CUSTOMER_ID}"
        )

        print(
            f"Account: {account_id}"
        )

        before_count = (
            count_customer_transactions(
                connection
            )
        )

        print(
            f"Transactions before seed: "
            f"{before_count}"
        )

        transactions = (
            generate_transactions(
                account_id
            )
        )

        inserted_count = (
            insert_transactions(
                connection,
                transactions,
            )
        )

        connection.commit()

        after_count = (
            count_customer_transactions(
                connection
            )
        )

        print(
            f"Generated history records: "
            f"{len(transactions)}"
        )

        print(
            f"Inserted records: "
            f"{inserted_count}"
        )

        print(
            f"Transactions after seed: "
            f"{after_count}"
        )

        if inserted_count == 0:
            print(
                "No new rows inserted. "
                "Historical seed data already exists."
            )

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    main()