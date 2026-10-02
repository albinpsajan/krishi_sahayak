"""
SubsidyChain feature (docs/features/subsidies.md).

Purpose
-------
Personalized subsidy discovery, application, deterministic eligibility
screening and officer decision workflow. Deliberately self-contained:
changes here must not touch irrigation, documents or profile logic
(docs/architecture.md sections 2 & 14).

Flow (docs/architecture.md section 3):
    Officer-managed scheme database
        -> eligibility rules (deterministic)
        -> deterministic matcher / risk screening
        -> AI explanation (only, never amounts/rules)
        -> farmer interface
"""

from apps.subsidies import models, schemas  # noqa: F401
from apps.subsidies.services import (  # noqa: F401
    subsidy_matcher,
    eligibility_checker,
    document_checker,
)
