import pandas as pd


def export_to_excel(output, path: str):
    """Exporte le classement des candidats + le détail des compétences dans un fichier Excel.

    `output` : liste de tuples (name, matching, evidence, recommendation, alerts, questions, skills)
    comme produit par la boucle d'analyse du dashboard.
    """
    ranking_rows = [{
        "Candidat": name,
        "Matching (%)": matching,
        "Evidence (%)": evidence,
        "Recommandation": recommendation,
        "Nb alertes": len(alerts),
    } for name, matching, evidence, recommendation, alerts, questions, skills in output]

    detail_rows = []
    for name, matching, evidence, recommendation, alerts, questions, skills in output:
        for s in skills:
            if not (s.required or s.preferred or s.declared):
                continue
            real_evidence = [e for e in s.evidence if e.source != "Compétences"]
            best_quote = real_evidence[0].quote if real_evidence else (s.evidence[0].quote if s.evidence else "")
            detail_rows.append({
                "Candidat": name,
                "Compétence": s.skill,
                "Type": "Requise" if s.required else ("Souhaitée" if s.preferred else "Autre"),
                "Déclarée": "Oui" if s.declared else "Non",
                "Verdict": s.verdict,
                "Confiance (%)": round(s.confidence * 100),
                "Durée identifiable (ans)": s.duration_years,
                "Preuve principale": best_quote,
            })

    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        pd.DataFrame(ranking_rows).sort_values("Matching (%)", ascending=False).to_excel(
            writer, sheet_name="Classement", index=False
        )
        pd.DataFrame(detail_rows).to_excel(writer, sheet_name="Détail compétences", index=False)

    return path
