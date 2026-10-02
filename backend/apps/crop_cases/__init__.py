"""
Crop Cases & CropDoctor feature (docs/features/crop-cases.md).

Purpose
-------
Farmers submit crop health cases with photos; the AI layer produces a
preliminary assessment; the Agricultural Officer verifies or corrects it
(human-in-the-loop). Owns the CropCase, CropImage, AIAssessment, OfficerReview
and Recommendation tables.
"""

from apps.crop_cases import models, schemas  # noqa: F401
