CREATE OR REPLACE TRIGGER item_audit
AFTER INSERT OR UPDATE OR DELETE ON finance.personal.item
FOR EACH ROW
EXECUTE FUNCTION finance.personal.audit_changes();