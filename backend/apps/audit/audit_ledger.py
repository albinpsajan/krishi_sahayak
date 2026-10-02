"""
Tamper-evident audit ledger (SHA-256 hash chain).

log_audit_action() appends an immutable record; verify_ledger_integrity()
re-walks the chain to prove no record was modified or removed.
"""

import hashlib
import json
from datetime import datetime

from apps.audit.models import AuditRecord

GENESIS_HASH = "0" * 64


def calculate_hash(
    actor_id: int,
    actor_role: str,
    action: str,
    target_type: str,
    target_id: str,
    timestamp_str: str,
    metadata_str: str,
    prev_hash: str,
) -> str:
    """Stable SHA-256 over the record's fields plus the previous record's hash."""
    payload = f"{actor_id}|{actor_role}|{action}|{target_type}|{target_id}|{timestamp_str}|{metadata_str}|{prev_hash}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def log_audit_action(
    db,
    actor_id: int,
    actor_name: str,
    actor_role: str,
    action: str,
    target_type: str,
    target_id: str,
    metadata: dict = None,
) -> AuditRecord:
    """Appends an immutable audit record to the cryptographic hash chain."""
    last_record = db.query(AuditRecord).order_by(AuditRecord.id.desc()).first()
    prev_hash = last_record.current_hash if last_record else GENESIS_HASH

    now = datetime.utcnow()
    timestamp_str = now.isoformat()
    metadata_str = json.dumps(metadata or {}, sort_keys=True)

    current_hash = calculate_hash(
        actor_id=actor_id,
        actor_role=actor_role,
        action=action,
        target_type=target_type,
        target_id=target_id,
        timestamp_str=timestamp_str,
        metadata_str=metadata_str,
        prev_hash=prev_hash,
    )

    record = AuditRecord(
        actor_id=actor_id,
        actor_name=actor_name,
        actor_role=actor_role,
        action=action,
        target_type=target_type,
        target_id=str(target_id),
        timestamp=now,
        metadata_json=metadata_str,
        prev_hash=prev_hash,
        current_hash=current_hash,
    )

    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def verify_ledger_integrity(db) -> dict:
    """Verifies that no record in the audit chain has been modified or removed."""
    records = db.query(AuditRecord).order_by(AuditRecord.id.asc()).all()
    if not records:
        return {"status": "VALID", "total_records": 0, "corrupted_record_id": None}

    expected_prev_hash = GENESIS_HASH
    for rec in records:
        if rec.prev_hash != expected_prev_hash:
            return {
                "status": "TAMPERED",
                "total_records": len(records),
                "corrupted_record_id": rec.id,
                "reason": f"Record #{rec.id} prev_hash mismatch",
            }

        recalculated_hash = calculate_hash(
            actor_id=rec.actor_id,
            actor_role=rec.actor_role,
            action=rec.action,
            target_type=rec.target_type,
            target_id=rec.target_id,
            timestamp_str=rec.timestamp.isoformat(),
            metadata_str=rec.metadata_json or "{}",
            prev_hash=rec.prev_hash,
        )

        if recalculated_hash != rec.current_hash:
            return {
                "status": "TAMPERED",
                "total_records": len(records),
                "corrupted_record_id": rec.id,
                "reason": f"Record #{rec.id} data modified, signature hash invalid",
            }

        expected_prev_hash = rec.current_hash

    return {
        "status": "VALID",
        "total_records": len(records),
        "corrupted_record_id": None,
        "latest_hash": expected_prev_hash,
    }
