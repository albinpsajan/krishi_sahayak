"""
Application-wide logging setup (docs/architecture.md section 9).

Log lines are tagged by feature, e.g.:
    [SUBSIDY_MATCH] schemes_checked=18 potential_matches=3 missing_docs=2

Rules:
  - Log identifiers only (user_id, case_number, application_number).
  - NEVER log phone numbers, addresses, document contents or tokens.
"""

import logging
import sys

_CONFIGURED = False


def configure_logging(level=logging.INFO):
    """Idempotently installs a stdout handler with a concise format."""
    global _CONFIGURED
    if _CONFIGURED:
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%H:%M:%S")
    )
    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)
