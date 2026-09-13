import re
from app.skills import SKILLS
from app.models import JobRequirement

# Marqueurs utilisés pour classifier les compétences trouvées dans le contexte.
REQUIRED_MARKERS = [
    "obligatoire", "obligatoires", "impératif", "impérative", "impératives",
    "indispensable", "indispensables", "exigé", "exigée", "exigées",
    "requis", "requise", "requises", "must have", "required",
    "vous maîtrisez", "vous maitrisez", "doit maîtriser", "doit maitriser",
    "doivent maîtriser", "doivent maitriser", "maîtrise de", "maitrise de",
    "compétences requises", "technologies requises",
]

PREFERRED_MARKERS = [
    "un plus", "un atout", "apprécié", "appréciée", "appréciées",
    "souhaité", "souhaitée", "souhaitées", "souhaitable", "serait un atout",
    "idéalement", "de préférence", "nice to have", "preferred",
    "compétences souhaitées", "technologies souhaitées", "compétences appréciées",
]

REQUIRED_HEADINGS = [
    "compétences obligatoires", "compétence obligatoire",
    "compétences requises", "compétence requise",
    "compétences indispensables", "compétence indispensable",
    "compétences nécessaires", "compétence nécessaire",
    "technologies obligatoires", "technologies requises",
    "must have", "required skills", "required technologies",
]

PREFERRED_HEADINGS = [
    "compétences souhaitées", "compétence souhaitée",
    "compétences appréciées", "compétence appréciée",
    "compétences complémentaires", "compétence complémentaire",
    "technologies souhaitées", "technologies appréciées",
    "nice to have", "preferred skills", "preferred technologies",
]

YEARS_PATTERN = re.compile(
    r"(\d+)\s*(?:\+)?\s*(?:ans|années|years)\s+d[’']?\s*exp[ée]rience",
    re.IGNORECASE,
)

SENIORITY_KEYWORDS = {
    "junior": ["junior", "débutant"],
    "confirmé": ["confirmé", "intermédiaire"],
    "senior": ["senior"],
    "expert": ["expert", "lead", "architecte", "staff"],
}


def _sentences(text):
    return [s for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]


def _normalize(text):
    """Normalise légèrement le texte pour rendre la détection des titres robuste."""
    text = text.lower().replace("’", "'")
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip(" :\t-–—•*")


def _heading_type(line):
    """Retourne required/preferred si la ligne est clairement un titre de section."""
    normalized = _normalize(line)
    # On accepte un titre avec ou sans ':' et avec une ponctuation de liste.
    normalized = re.sub(r"\s*[:：]\s*$", "", normalized)
    if normalized in REQUIRED_HEADINGS:
        return "required"
    if normalized in PREFERRED_HEADINGS:
        return "preferred"
    return None


def _section_contexts(text):
    """
    Associe chaque ligne à une section 'required' ou 'preferred'.
    Exemple accepté:
        COMPÉTENCES OBLIGATOIRES
        Java
        Spring Boot

        COMPÉTENCES SOUHAITÉES
        AWS
        Docker
    """
    lines = text.splitlines()
    contexts = []
    current = None

    for line in lines:
        heading = _heading_type(line)
        if heading:
            current = heading
            # Le titre lui-même fait aussi partie du contexte : utile pour
            # les cas 'Compétences obligatoires : Java, SQL'.
            contexts.append((line, current))
            continue

        # Un nouveau grand titre non lié aux compétences termine la section.
        stripped = line.strip()
        if current and stripped and not line[:1].isspace():
            # On ne coupe pas sur une simple ligne de compétence.
            # On coupe surtout sur des titres explicites.
            norm = _normalize(stripped)
            if (
                re.match(r"^(missions?|responsabilit|profil|poste|formation|expérience|experience|contexte|description)\b", norm)
                and not any(a in norm for d in SKILLS.values() for a in d["aliases"] if len(a) >= 3)
            ):
                current = None

        contexts.append((line, current))

    return contexts


def _alias_in_text(text, alias):
    # Évite par exemple que 'go' soit détecté dans 'google'.
    pattern = r"(?<![\w])" + re.escape(alias.lower()) + r"(?![\w])"
    return re.search(pattern, text.lower()) is not None


def _classify_skill(skill, aliases, job_text, contexts):
    """Retourne (required, preferred, nb_contextes) pour une compétence."""
    occurrences = []
    for line, section in contexts:
        if any(_alias_in_text(line, alias) for alias in aliases):
            occurrences.append((line, section))

    # Rechercher aussi dans les phrases : couvre les offres rédigées en prose.
    matched_sentences = [
        s for s in _sentences(job_text)
        if any(_alias_in_text(s, alias) for alias in aliases)
    ]

    required_by_section = any(section == "required" for _, section in occurrences)
    preferred_by_section = any(section == "preferred" for _, section in occurrences)

    required_by_marker = any(
        any(m in s.lower() for m in REQUIRED_MARKERS) for s in matched_sentences
    )
    preferred_by_marker = any(
        any(m in s.lower() for m in PREFERRED_MARKERS) for s in matched_sentences
    )

    # La section explicite est prioritaire. Sinon on utilise les marqueurs
    # présents dans la phrase. Si rien ne qualifie la compétence, elle reste
    # requise par défaut (comportement historique).
    if required_by_section and not preferred_by_section:
        return True, False, max(1, len(occurrences))
    if preferred_by_section and not required_by_section:
        return False, True, max(1, len(occurrences))
    if preferred_by_marker and not required_by_marker:
        return False, True, max(1, len(matched_sentences))
    if required_by_marker:
        return True, False, max(1, len(matched_sentences))
    return True, False, max(1, len(matched_sentences))


def _is_shadowed_skill(skill, matched_skills):
    """Évite de remonter une compétence générique déjà couverte par une plus précise.
    Ex.: Spring Boot -> ne pas ajouter Spring ; SQL Server -> ne pas ajouter SQL.
    """
    base = _normalize(skill)
    for other in matched_skills:
        if other == skill:
            continue
        other_norm = _normalize(other)
        if len(other_norm) > len(base) and re.search(r"(?<![\\w])" + re.escape(base) + r"(?![\\w])", other_norm):
            return True
    return False


def parse_job_description(job_text: str) -> JobRequirement:
    job_text = job_text or ""
    low = job_text.lower()
    required, preferred = [], []
    skill_weights = {}
    contexts = _section_contexts(job_text)

    matched_skills = [
        skill for skill, data in SKILLS.items()
        if any(_alias_in_text(low, alias) for alias in data["aliases"])
    ]

    for skill, data in SKILLS.items():
        aliases = data["aliases"]
        if skill not in matched_skills:
            continue
        if _is_shadowed_skill(skill, matched_skills):
            continue

        is_required, is_preferred, occurrence_count = _classify_skill(
            skill, aliases, job_text, contexts
        )

        if is_preferred:
            preferred.append(skill)
        else:
            required.append(skill)

        # Poids indicatif : une compétence citée plusieurs fois ou explicitement
        # requise pèse davantage dans le score, sans dépasser 2.0.
        weight = 1.0 + 0.2 * (max(1, occurrence_count) - 1)
        if is_required:
            weight += 0.3
        skill_weights[skill] = round(min(2.0, weight), 2)

    years_match = YEARS_PATTERN.search(job_text)
    min_years = int(years_match.group(1)) if years_match else None

    seniority = ""
    for level, keywords in SENIORITY_KEYWORDS.items():
        if any(k in low for k in keywords):
            seniority = level
            break

    return JobRequirement(
        required_skills=required,
        preferred_skills=preferred,
        min_years_experience=min_years,
        seniority=seniority,
        raw_text=job_text,
        skill_weights=skill_weights,
    )
