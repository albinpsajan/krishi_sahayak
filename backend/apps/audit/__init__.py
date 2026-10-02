"""
Tamper-evident audit feature (docs/features/audit.md).

Purpose
-------
Cryptographically chained (SHA-256) append-only record of every important
action: registrations, case submissions, AI assessments, officer reviews and
subsidy decisions.
"""

from apps.audit import models, audit_ledger  # noqa: F401
