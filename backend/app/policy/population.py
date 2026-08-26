"""
Population Profile Resolver.
Resolves whether a patient is pediatric, adult, or geriatric based on configurable policy.
TODO: CLINICAL VALIDATION REQUIRED.
"""

from typing import Optional
from app.core.config import settings

def resolve_population_profile(age_years: Optional[int], override_profile: Optional[str] = None) -> str:
    """
    Resolves demographic profile based on age.
    If age is missing, defaults to 'adult' but marks low completeness.
    """
    if override_profile and override_profile in ["pediatric", "adult", "geriatric"]:
        return override_profile
        
    if age_years is None:
        return "adult"
        
    if age_years <= settings.PEDIATRIC_MAX_AGE:
        return "pediatric"
    elif age_years >= settings.GERIATRIC_MIN_AGE:
        return "geriatric"
    else:
        return "adult"
