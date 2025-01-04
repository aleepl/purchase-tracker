CREATE TRIGGER finance.personal.receipt_audit
AFTER INSERT OR UPDATE OR DELETE ON finance.personal.receipt
FOR EACH ROW
EXECUTE FUNCTION finance.personal.audit_changes();