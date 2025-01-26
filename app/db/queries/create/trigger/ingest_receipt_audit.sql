CREATE OR REPLACE TRIGGER receipt_audit
AFTER INSERT OR UPDATE OR DELETE ON finance.ingest.receipt
FOR EACH ROW
EXECUTE FUNCTION finance.ingest.audit_changes();