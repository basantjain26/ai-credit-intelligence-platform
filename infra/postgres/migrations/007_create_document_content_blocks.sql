CREATE TABLE document_content_blocks (
    block_id VARCHAR(100) PRIMARY KEY,

    document_id VARCHAR(100) NOT NULL,

    block_type VARCHAR(30) NOT NULL,

    text_content TEXT,

    table_content JSONB,

    page_number INTEGER,
    paragraph_index INTEGER,
    table_index INTEGER,
    sheet_name VARCHAR(255),
    row_number INTEGER,

    parser_name VARCHAR(100),
    parser_version VARCHAR(50),

    extracted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_content_block_document
        FOREIGN KEY (document_id)
        REFERENCES documents(document_id)
        ON DELETE CASCADE
);

CREATE INDEX idx_content_blocks_document
ON document_content_blocks(document_id);

CREATE INDEX idx_content_blocks_type
ON document_content_blocks(block_type);