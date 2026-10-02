"""
Document checker (deterministic, docs/architecture.md section 3).

Decides which mandatory scheme documents are present/missing from an
application's attached documents. Pure functions, no AI, no DB.

Matching strategy: a required document is satisfied when an uploaded document
shares a significant word with it (e.g. one combined "Aadhaar Card & Land
Certificate" upload satisfies both "Aadhaar Card" and "Land Record") or when
one name contains the other verbatim.
"""

import re

from apps.subsidies.services.eligibility_checker import MISSING_DOC_PENALTY

# Words too generic to prove a specific document type on their own
GENERIC_WORDS = {"and", "the", "for", "with", "from", "copy", "report", "record", "card", "certificate"}


def parse_required_documents(scheme: dict) -> list:
    """Parses the scheme's comma-separated required-documents text into a list."""
    req_docs_str = scheme.get("required_documents", "Aadhaar Card, Land Record")
    return [d.strip().lower() for d in req_docs_str.split(",") if d.strip()]


def _significant_words(doc_name: str) -> set:
    """Lowercased words of a document name, minus generic filler words."""
    words = re.findall(r"[a-z]+", doc_name.lower())
    return {w for w in words if len(w) >= 3 and w not in GENERIC_WORDS}


def document_satisfies_requirement(uploaded_name: str, required_name: str) -> bool:
    """True when an uploaded document plausibly proves a required document."""
    uploaded_name = (uploaded_name or "").lower()
    required_name = (required_name or "").lower()
    if not uploaded_name:
        return False
    # Verbatim containment either way ("aadhaar card" ⊂ "aadhaar card & land certificate")
    if required_name in uploaded_name or uploaded_name in required_name:
        return True
    # Word overlap ("land record" ~ "land possession certificate" via 'land')
    return bool(_significant_words(required_name) & _significant_words(uploaded_name))


def find_missing_documents(scheme: dict, application_docs: list) -> list:
    """Returns required document names not satisfied by the application's docs."""
    required = parse_required_documents(scheme)
    uploaded = [doc.get("document_type", "") for doc in application_docs]

    missing = []
    for req in required:
        if not any(document_satisfies_requirement(up, req) for up in uploaded):
            missing.append(req)
    return missing


def document_penalty(missing_docs: list) -> int:
    """Score penalty applied when mandatory documents are missing."""
    return MISSING_DOC_PENALTY if missing_docs else 0
