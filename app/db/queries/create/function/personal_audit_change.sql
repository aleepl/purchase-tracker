CREATE OR REPLACE FUNCTION finance.personal.audit_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO finance.personal.audit_log (table_name, operation_type, changed_at, user_name, old_data)
        VALUES (TG_TABLE_NAME, TG_OP, CURRENT_TIMESTAMP, CURRENT_USER, row_to_json(OLD));
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO finance.personal.audit_log (table_name, operation_type, changed_at, user_name, new_data)
        VALUES (TG_TABLE_NAME, TG_OP, CURRENT_TIMESTAMP, CURRENT_USER, row_to_json(NEW));
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO finance.personal.audit_log (table_name, operation_type, changed_at, user_name, old_data, new_data)
        VALUES (TG_TABLE_NAME, TG_OP, CURRENT_TIMESTAMP, CURRENT_USER, row_to_json(OLD), row_to_json(NEW));
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
