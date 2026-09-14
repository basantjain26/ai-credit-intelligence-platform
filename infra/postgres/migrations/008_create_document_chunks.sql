CREATE EXTENSION IF NOT EXISTS vector;


CREATE TABLE IF NOT EXISTS document_chunks (

    chunk_id VARCHAR(100)
        PRIMARY KEY,

    document_id VARCHAR(100)
        NOT NULL,

    chunk_type VARCHAR(50)
        NOT NULL,

    chunk_text TEXT
        NOT NULL,

    page_number INTEGER,

    metadata JSONB
        NOT NULL
        DEFAULT '{}'::jsonb,

    embedding vector(1536),

    embedding_model VARCHAR(100),

    created_at TIMESTAMP
        NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_document_chunks_document
        FOREIGN KEY (document_id)
        REFERENCES documents(document_id)
        ON DELETE CASCADE
);


CREATE INDEX IF NOT EXISTS
idx_document_chunks_document
ON document_chunks(document_id);


CREATE INDEX IF NOT EXISTS
idx_document_chunks_type
ON document_chunks(chunk_type);

CREATE INDEX IF NOT EXISTS
idx_document_chunks_embedding_hnsw
ON document_chunks
USING hnsw (
    embedding vector_cosine_ops
);