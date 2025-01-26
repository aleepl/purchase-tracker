CREATE TABLE IF NOT EXISTS finance.ingest.audit_log (
    id INT NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    table_name VARCHAR(255) NOT NULL,
    operation_type VARCHAR(255) NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_name VARCHAR(255) DEFAULT CURRENT_USER,
    old_data JSONB,
    new_data JSONB
);

CREATE INDEX IF NOT EXISTS idx_audit_log_table_name ON finance.ingest.audit_log (table_name);
