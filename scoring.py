from app.questions import generate_questions


def score_candidate(skill_results, required_skills, preferred_skills=None, min_years_experience=None,
                     candidate_years=None, skill_weights=None, consistency_alerts=None):
    preferred_skills = preferred_skills or []
    skill_weights = skill_weights or {}
    req = {s.lower(): s for s in required_skills}
    pref = {s.lower(): s for s in preferred_skills}

    matching = 0.0
    evidence_values = []

    for r in skill_results:
        key = r.skill.lower()
        weight = skill_weights.get(r.skill, 1.0)
        if key in req:
            r.required = True
            matching += weight * r.confidence
            evidence_values.append(r.confidence)
        elif key in pref:
            r.preferred = True
            matching += 0.5 * weight * r.confidence
            evidence_values.append(r.confidence)

    max_score = sum(skill_weights.get(s, 1.0) for s in required_skills) + \
        0.5 * sum(skill_weights.get(s, 1.0) for s in preferred_skills)
    matching_score = round(100 * matching / max_score, 1) if max_score else 0.0
    evidence_score = round(100 * sum(evidence_values) / len(evidence_values), 1) if evidence_values else 0.0

    alerts = list(consistency_alerts or [])
    for r in skill_results:
        if r.verdict == "VERIFY" and r.declared and (r.required or r.preferred):
            alerts.append(f"{r.skill} : compétence déclarée mais preuve insuffisante dans les expériences/projets.")
        elif r.verdict == "NOT_DEMONSTRATED" and r.required:
            alerts.append(f"{r.skill} : compétence requise non démontrée dans le CV.")

    if min_years_experience and candidate_years is not None and candidate_years < min_years_experience:
        alerts.append(
            f"Ancienneté estimée ({candidate_years} ans) inférieure au seuil demandé ({min_years_experience} ans)."
        )

    questions = generate_questions(skill_results)

    if matching_score >= 80 and evidence_score >= 75 and not any("Ancienneté" in a for a in alerts):
        recommendation = "ENTRETIEN"
    elif matching_score >= 65:
        recommendation = "À QUALIFIER"
    else:
        recommendation = "FAIBLE MATCHING"

    return matching_score, evidence_score, alerts, questions, recommendation
