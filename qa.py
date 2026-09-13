from app.evidence import VERDICT_LABELS
from app.llm import rephrase_evidence_answer


def ask_about_skill(skill_result, use_llm: bool = False) -> str:
    """Répond à la question type : 'Le candidat a-t-il réellement utilisé X en contexte professionnel ?'

    Reproduit le format cible : verdict, % de confiance, citations du CV, durée identifiable.
    """
    r = skill_result
    lines = []

    if r.verdict == "CONFIRMED":
        lines.append(f"Oui — confiance {int(r.confidence * 100)}%.")
    elif r.verdict == "PROBABLE":
        lines.append(f"Probablement — confiance {int(r.confidence * 100)}%.")
    elif r.verdict == "VERIFY":
        lines.append(f"À vérifier en entretien — confiance {int(r.confidence * 100)}%.")
    else:
        lines.append(f"Non démontré — confiance {int(r.confidence * 100)}%.")

    real_evidence = [e for e in r.evidence if e.source != "Compétences"]
    if real_evidence:
        for e in real_evidence[:3]:
            period = f" ({e.period})" if e.period else ""
            lines.append(f"{e.source}{period} : {e.quote}")
        if r.duration_years:
            lines.append(f"Durée professionnelle identifiable : environ {r.duration_years} an(s).")
    elif r.declared:
        lines.append(
            f"{r.skill} apparaît dans la section « Compétences », mais aucune expérience ou "
            f"projet détaillé ne permet de confirmer son utilisation professionnelle."
        )
    else:
        lines.append(f"{r.skill} n'apparaît nulle part dans le CV analysé.")

    answer = "\n".join(lines)
    if use_llm:
        answer = rephrase_evidence_answer(answer, r.skill)
    return answer
