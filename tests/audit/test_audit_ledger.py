import unittest

import tests.test_environment  # noqa: F401

from apps.audit.audit_ledger import GENESIS_HASH, log_audit_action, verify_ledger_integrity
from apps.audit.models import AuditRecord
from core.database import Base, SessionLocal, engine


class AuditLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.db = SessionLocal()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_append_records_chain_valid(self):
        log_audit_action(
            self.db, actor_id=999, actor_name="Test Farmer", actor_role="FARMER",
            action="TEST_ACTION", target_type="TEST", target_id="1", metadata={"k": "v"},
        )
        log_audit_action(
            self.db, actor_id=998, actor_name="Test Officer", actor_role="OFFICER",
            action="TEST_ACTION_2", target_type="TEST", target_id="2",
        )
        status = verify_ledger_integrity(self.db)
        self.assertEqual(status["status"], "VALID")
        self.assertGreaterEqual(status["total_records"], 2)

    def test_first_record_links_to_genesis(self):
        first = self.db.query(AuditRecord).order_by(AuditRecord.id.asc()).first()
        self.assertEqual(first.prev_hash, GENESIS_HASH)

    def test_each_record_links_to_previous(self):
        records = self.db.query(AuditRecord).order_by(AuditRecord.id.asc()).all()
        for prev, cur in zip(records, records[1:]):
            self.assertEqual(cur.prev_hash, prev.current_hash)

    def test_tamper_detection(self):
        records = self.db.query(AuditRecord).order_by(AuditRecord.id.asc()).all()
        target = records[-1]
        original = target.action
        try:
            target.action = "TAMPERED_ACTION"
            self.db.commit()
            status = verify_ledger_integrity(self.db)
            self.assertEqual(status["status"], "TAMPERED")
            self.assertEqual(status["corrupted_record_id"], target.id)
        finally:
            target.action = original
            self.db.commit()


if __name__ == "__main__":
    unittest.main()
