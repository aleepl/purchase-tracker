CREATE OR REPLACE TRIGGER purchase_audit
AFTER INSERT OR UPDATE OR DELETE ON finance.personal.purchase
FOR EACH ROW
EXECUTE FUNCTION finance.personal.audit_changes();