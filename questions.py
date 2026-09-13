def generate_questions(skill_results):
    """Génère des questions d'entretien ciblées en fonction du verdict de chaque compétence."""
    questions = []
    for r in skill_results:
        if not (r.required or r.preferred):
            continue
        if r.verdict == "VERIFY":
            questions.append(
                f"Vous mentionnez {r.skill} dans vos compétences : pouvez-vous décrire un projet concret "
                f"où vous l'avez utilisé et votre contribution personnelle ?"
            )
        elif r.verdict == "PROBABLE":
            questions.append(
                f"Vous avez utilisé {r.skill} sur une expérience : pouvez-vous détailler le contexte, "
                f"la durée et le niveau de responsabilité sur cette technologie ?"
            )
        elif r.verdict == "CONFIRMED" and r.duration_years >= 3:
            questions.append(
                f"Vous avez environ {r.duration_years} ans d'expérience identifiable en {r.skill} : "
                f"quel a été le projet le plus complexe réalisé avec cette technologie ?"
            )
        elif r.verdict == "NOT_DEMONSTRATED" and r.required:
            questions.append(
                f"{r.skill} est requis pour ce poste mais n'apparaît pas dans votre CV : "
                f"avez-vous une expérience non mentionnée sur cette technologie ?"
            )
    return questions
