"""
AutoClerk feature (docs/features/autoclerk.md).

Purpose
-------
Synthesizes the structured official administrative report (markdown) for the
Agricultural Officer from a crop case, farmer profile, AI assessment and
officer review. Formatting only - it invents no facts.
"""

from apps.autoclerk import autoclerk_service  # noqa: F401
