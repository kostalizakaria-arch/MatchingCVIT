"""Point d'intégration LLM (optionnel).

Le moteur déterministe (evidence.py, job_parser.py, qa.py) fonctionne seul,
sans clé API : c'est le comportement par défaut, comme en V1.

Si une clé ANTHROPIC_API_KEY est présente dans l'environnement et le paquet
`anthropic` installé, ce module peut être utilisé pour reformuler les réponses
de l'Evidence Engine en langage plus naturel, ou pour renforcer l'extraction
de compétences dans des CV mal structurés (synonymes, formulations implicites).

Toute erreur (pas de clé, pas de réseau, paquet absent) fait retomber
silencieusement sur le moteur déterministe : l'IA générative est un bonus,
jamais une dépendance bloquante.
"""

import os

LLM_AVAILABLE = False
try:
    import anthropic  # noqa: F401
    LLM_AVAILABLE = bool(os.environ.get("ANTHROPIC_API_KEY"))
except ImportError:
    LLM_AVAILABLE = False


def call_llm(prompt: str, max_tokens: int = 400) -> str:
    """Appelle le modèle si configuré, sinon lève NotImplementedError."""
    if not LLM_AVAILABLE:
        raise NotImplementedError("Provider LLM non configuré (ANTHROPIC_API_KEY absente).")
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in response.content if block.type == "text")


def rephrase_evidence_answer(deterministic_answer: str, skill: str) -> str:
    """Reformule la réponse déterministe en langage plus naturel via le LLM, si disponible."""
    if not LLM_AVAILABLE:
        return deterministic_answer
    try:
        prompt = (
            f"Reformule cette analyse de preuve de compétence '{skill}' pour un recruteur, "
            f"en gardant exactement les mêmes faits, le même verdict et la même confiance, "
            f"en français, de façon concise (3-4 lignes maximum) :\n\n{deterministic_answer}"
        )
        return call_llm(prompt)
    except Exception:
        return deterministic_answer


def extract_experiences_llm(cv_text: str):
    """Extraction structurée des expériences/projets via LLM (remplace le regex de périodes
    quand une clé API est configurée — plus robuste sur les CV mal formatés ou multilingues).

    Retourne une liste de dicts {period, start_year, end_year, is_project, text}
    ou None si le LLM n'est pas disponible / la réponse n'est pas exploitable.
    Ne lève jamais d'exception : en cas de doute, on retombe sur le moteur regex.
    """
    if not LLM_AVAILABLE:
        return None
    try:
        import json
        prompt = (
            "Découpe ce CV en blocs d'expérience professionnelle ou de projet. "
            "Réponds UNIQUEMENT avec un tableau JSON, sans texte autour, sans balises markdown. "
            "Chaque élément : {\"period\": \"AAAA-AAAA\", \"start_year\": int, \"end_year\": int, "
            "\"is_project\": bool, \"text\": \"texte intégral du bloc, verbatim\"}. "
            "Si aucune période n'est identifiable pour un bloc, mets start_year et end_year à null.\n\n"
            f"CV :\n{cv_text[:6000]}"
        )
        raw = call_llm(prompt, max_tokens=2000)
        cleaned = raw.strip().strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        data = json.loads(cleaned)
        if not isinstance(data, list):
            return None
        return data
    except Exception:
        return None
