from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ExperienceBlock:
    """Un bloc de texte du CV rattaché à une période identifiée (expérience ou projet)."""
    text: str
    period_label: str = ""
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    duration_years: float = 0.0
    is_project: bool = False


@dataclass
class Evidence:
    skill: str
    source: str          # "Expérience", "Projet" ou "Compétences"
    quote: str
    strength: float
    period: str = ""


@dataclass
class SkillResult:
    skill: str
    declared: bool
    evidence: List[Evidence] = field(default_factory=list)
    confidence: float = 0.0
    verdict: str = "NOT_DEMONSTRATED"   # CONFIRMED / PROBABLE / VERIFY / NOT_DEMONSTRATED
    duration_years: float = 0.0
    required: bool = False
    preferred: bool = False


@dataclass
class JobRequirement:
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    min_years_experience: Optional[int] = None
    seniority: str = ""   # junior / confirmé / senior / expert
    raw_text: str = ""
    skill_weights: dict = field(default_factory=dict)


@dataclass
class CandidateResult:
    name: str
    matching_score: float
    evidence_score: float
    skills: List[SkillResult]
    alerts: List[str]
    questions: List[str]
    recommendation: str
