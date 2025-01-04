CREATE TRIGGER finance.personal.product_audit
AFTER INSERT OR UPDATE OR DELETE ON finance.personal.product
FOR EACH ROW
EXECUTE FUNCTION finance.personal.audit_changes();