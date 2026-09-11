CREATE TABLE documents (
    document_id VARCHAR(100) PRIMARY KEY,
    customer_id VARCHAR(50),
    application_id VARCHAR(50),

    document_type VARCHAR(100),
    document_name VARCHAR(255) NOT NULL,
    file_format VARCHAR(20) NOT NULL,

    source_path TEXT NOT NULL,
    file_size_bytes BIGINT,
    checksum_sha256 VARCHAR(64) NOT NULL,

    processing_status VARCHAR(50) NOT NULL DEFAULT 'INGESTED',

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_document_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),

    CONSTRAINT fk_document_application
        FOREIGN KEY (application_id)
        REFERENCES loan_applications(application_id),

    CONSTRAINT uq_document_checksum
        UNIQUE (checksum_sha256)
);