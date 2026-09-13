import re
from app.skills import SKILLS
from app.models import Evidence, SkillResult
from app.experience_extractor import extract_experience_blocks

EXPERIENCE_MARKERS = [
    "expérience", "experience", "projet", "mission", "responsabil",
    "développement", "developpement", "conception", "maintenance",
    "mise en place", "implementation", "implémentation", "utilisation", "réalisation",
]

VERDICT_LABELS = {
    "CONFIRMED": "🟢 CONFIRMÉ",
    "PROBABLE": "🟡 PROBABLE",
    "VERIFY": "🟠 À VÉRIFIER",
    "NOT_DEMONSTRATED": "🔴 NON DÉMONTRÉ",
}


def _sentences(text):
    return [s for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]


def analyze_skill(skill: str, text: str, blocks=None) -> SkillResult:
    low = text.lower()
    aliases = SKILLS[skill]["aliases"]
    declared = any(a in low for a in aliases)
    blocks = blocks if blocks is not None else extract_experience_blocks(text)

    evidence = []
    duration = 0.0
    for block in blocks:
        source = "Projet" if block.is_project else ("Expérience" if block.period_label else "Compétences")
        for sentence in _sentences(block.text):
            s_low = sentence.lower().strip()
            if not any(a in s_low for a in aliases):
                continue
            has_period = bool(block.period_label)
            context_bonus = 0.35 if any(m in s_low for m in EXPERIENCE_MARKERS) else 0.05
            period_bonus = 0.15 if has_period else 0.0
            strength = min(1.0, 0.40 + context_bonus + period_bonus)
            evidence.append(Evidence(skill, source, sentence.strip()[:350], strength, block.period_label))
            if has_period and source != "Compétences":
                duration += block.duration_years / max(1, len(_sentences(block.text)) and 1)

    # Durée = somme des durées des blocs distincts où la compétence apparaît réellement (pas par phrase)
    distinct_blocks = {b.period_label: b.duration_years for b in blocks
                        if b.period_label and any(a in b.text.lower() for a in aliases)}
    duration = round(sum(distinct_blocks.values()), 1)

    real_evidence = [e for e in evidence if e.source != "Compétences"]

    if len(real_evidence) >= 2 or (len(real_evidence) == 1 and duration >= 2):
        confidence = min(0.98, 0.75 + 0.05 * len(real_evidence) + 0.02 * duration)
        verdict = "CONFIRMED"
    elif len(real_evidence) == 1:
        confidence = 0.70
        verdict = "PROBABLE"
    elif declared:
        confidence = 0.22
        verdict = "VERIFY"
    else:
        confidence = 0.0
        verdict = "NOT_DEMONSTRATED"

    return SkillResult(skill, declared, evidence, round(confidence, 2), verdict, duration_years=duration)


def best_evidence(skill_result, n=2):
    """Retourne les preuves les plus parlantes (expérience/projet avant simple liste de compétences)."""
    real = [e for e in skill_result.evidence if e.source != "Compétences"]
    return (real or skill_result.evidence)[:n]


def analyze_skills(text, skills=None):
    skills = skills or list(SKILLS)
    blocks = extract_experience_blocks(text)
    return [analyze_skill(skill, text, blocks) for skill in skills]
