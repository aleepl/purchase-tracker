CREATE TABLE IF NOT EXISTS finance.personal.audit_log (
    id INT NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    table_name TEXT NOT NULL,
    operation_type TEXT NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_name TEXT DEFAULT CURRENT_USER,
    old_data JSONB,
    new_data JSONB
);

CREATE INDEX idx_audit_log_table_name ON finance.personal.audit_log (table_name);
