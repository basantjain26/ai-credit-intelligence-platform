ALTER TABLE documents
ADD COLUMN classification_method VARCHAR(50),
ADD COLUMN classification_confidence NUMERIC(5,4),
ADD COLUMN classified_at TIMESTAMP;

ALTER TABLE documents
ADD CONSTRAINT chk_classification_confidence
CHECK (
    classification_confidence IS NULL
    OR (
        classification_confidence >= 0
        AND classification_confidence <= 1
    )
);