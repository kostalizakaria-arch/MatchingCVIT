import re
from datetime import datetime
from app.models import ExperienceBlock
from app.llm import LLM_AVAILABLE, extract_experiences_llm

CURRENT_YEAR = datetime.now().year

# Repère une période du type "2022-2025", "2022 à 2026", "01/2022 - 12/2025", "depuis 2023"
PERIOD_PATTERN = re.compile(
    r"(?:depuis\s+)?(\d{4})\s*(?:-|–|à|to)\s*(\d{4}|aujourd'hui|présent|present|now)",
    re.IGNORECASE,
)
SINGLE_YEAR_SINCE = re.compile(r"depuis\s+(\d{4})", re.IGNORECASE)

PROJECT_MARKERS = ["projet", "project"]


def _parse_end(token: str) -> int:
    if token.lower() in ("aujourd'hui", "présent", "present", "now"):
        return CURRENT_YEAR
    return int(token)


def extract_experience_blocks(text: str):
    """Découpe le CV en blocs autour de chaque période détectée.

    Essaie d'abord une extraction LLM (plus robuste sur les CV mal formatés
    ou multilingues) si une clé API est configurée ; retombe automatiquement
    sur le découpage par regex sinon ou en cas d'échec/réponse inexploitable.
    """
    if LLM_AVAILABLE:
        llm_blocks = _blocks_from_llm(text)
        if llm_blocks:
            return llm_blocks
    return _extract_experience_blocks_regex(text)


def _blocks_from_llm(text: str):
    data = extract_experiences_llm(text)
    if not data:
        return None
    blocks = []
    try:
        for item in data:
            start = item.get("start_year")
            end = item.get("end_year")
            duration = max(0.5, end - start) if (start and end) else 0.0
            blocks.append(ExperienceBlock(
                text=item.get("text", ""),
                period_label=item.get("period", "") or "",
                start_year=start,
                end_year=end,
                duration_years=duration,
                is_project=bool(item.get("is_project", False)),
            ))
        return blocks or None
    except (AttributeError, TypeError):
        return None


def _extract_experience_blocks_regex(text: str):
    matches = list(PERIOD_PATTERN.finditer(text))
    if not matches:
        since = SINGLE_YEAR_SINCE.search(text)
        if since:
            start = int(since.group(1))
            return [ExperienceBlock(
                text=text, period_label=f"depuis {start}",
                start_year=start, end_year=CURRENT_YEAR,
                duration_years=max(0.5, CURRENT_YEAR - start),
            )]
        return [ExperienceBlock(text=text, period_label="", duration_years=0.0)]

    blocks = []
    for i, m in enumerate(matches):
        start_year = int(m.group(1))
        end_year = _parse_end(m.group(2))
        segment_start = m.start()
        segment_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        segment_text = text[segment_start:segment_end]
        lookback = text[max(0, segment_start - 40):segment_start]
        is_project = any(p in (lookback + segment_text[:120]).lower() for p in PROJECT_MARKERS)
        duration = max(0.5, end_year - start_year)
        blocks.append(ExperienceBlock(
            text=segment_text,
            period_label=f"{start_year}–{end_year}",
            start_year=start_year,
            end_year=end_year,
            duration_years=duration,
            is_project=is_project,
        ))

    # Texte avant la première période détectée (souvent la section "Compétences")
    header = text[:matches[0].start()]
    if header.strip():
        blocks.insert(0, ExperienceBlock(text=header, period_label="", duration_years=0.0))

    return blocks


def total_years_experience(blocks):
    """Estime l'ancienneté totale en fusionnant les plages d'années (évite les doublons)."""
    years = set()
    for b in blocks:
        if b.start_year and b.end_year:
            years.update(range(b.start_year, b.end_year + 1))
    return len(years)


def chronology_alerts(blocks):
    """Détecte les chevauchements de périodes entre expériences (hors projets) à vérifier en entretien.

    Un chevauchement n'est pas nécessairement une anomalie (freelance, cumul d'activités),
    d'où une formulation prudente : un signal à vérifier, jamais une accusation.
    """
    experiences = [b for b in blocks if b.start_year and b.end_year and not b.is_project]
    alerts = []
    for i in range(len(experiences)):
        for j in range(i + 1, len(experiences)):
            a, b = experiences[i], experiences[j]
            overlap = min(a.end_year, b.end_year) - max(a.start_year, b.start_year)
            if overlap > 0:
                alerts.append(
                    f"Chevauchement de périodes à vérifier : {a.period_label} et {b.period_label} "
                    f"se recoupent sur environ {overlap} an(s)."
                )
    return alerts
