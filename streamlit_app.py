import io
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from app.parser import extract_text
from app.evidence import analyze_skills, VERDICT_LABELS, best_evidence
from app.experience_extractor import extract_experience_blocks, total_years_experience, chronology_alerts
from app.job_parser import parse_job_description
from app.scoring import score_candidate
from app.qa import ask_about_skill
from app.export import export_to_excel
from app.llm import LLM_AVAILABLE
from app.demo import DEMO_JOB_TEXT, run_demo
from app.skills import all_skill_names, add_custom_skill, SKILLS

APP_NAME = "MatchingCVIT"

st.set_page_config(page_title=APP_NAME, page_icon="🎯", layout="wide", initial_sidebar_state="expanded")

# ----------------------------- Etat persistant -----------------------------
def init_state():
    defaults = {
        "mode": "Démo",
        "job_text": DEMO_JOB_TEXT,
        "required": [],
        "preferred": [],
        "last_parsed_job_text": None,
        "candidate_files": [],
        "last_output": None,
        "demo_results": None,
        "custom_skill_input": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_state()

# ----------------------------- Style -----------------------------
st.markdown("""
<style>
    :root {
        --mcv-primary: #0f766e;
        --mcv-primary-dark: #0b5a54;
        --mcv-primary-bg: #ecfdf9;
        --mcv-ink: #0f172a;
        --mcv-muted: #64748b;
        --mcv-border: #e2e8f0;
        --mcv-green: #15803d; --mcv-green-bg: #dcfce7;
        --mcv-amber: #b45309; --mcv-amber-bg: #fef3c7;
        --mcv-red: #b91c1c; --mcv-red-bg: #fee2e2;
    }
    .main .block-container {padding-top: 1.3rem; padding-bottom: 3rem; max-width: 1200px;}

    .mcv-header {
        display: flex; align-items: center; gap: 14px;
        padding: 1.1rem 1.3rem; border-radius: 16px; margin-bottom: 1.4rem;
        background: #ffffff; border: 1px solid var(--mcv-border);
        box-shadow: 0 1px 3px rgba(15,23,42,.04);
    }
    .mcv-logo {
        width: 46px; height: 46px; border-radius: 12px; flex-shrink: 0;
        background: var(--mcv-primary); color: white; font-weight: 700; font-size: 1.05rem;
        display: flex; align-items: center; justify-content: center;
    }
    .mcv-header h1 {margin: 0; font-size: 1.5rem; color: var(--mcv-ink); font-weight: 700;}
    .mcv-header p {margin: .15rem 0 0; color: var(--mcv-muted); font-size: .92rem;}
    .mcv-status {
        margin-left: auto; padding: 5px 14px; border-radius: 999px; font-size: .82rem; font-weight: 600;
        white-space: nowrap;
    }
    .mcv-status.on { background: var(--mcv-green-bg); color: var(--mcv-green); }
    .mcv-status.off { background: #f1f5f9; color: var(--mcv-muted); }

    .mcv-pill {display:inline-block; padding: 3px 12px; border-radius: 999px; font-size: .8rem; font-weight: 700;}
    .mcv-pill.entretien {background: var(--mcv-green-bg); color: var(--mcv-green);}
    .mcv-pill.qualifier {background: var(--mcv-amber-bg); color: var(--mcv-amber);}
    .mcv-pill.faible {background: var(--mcv-red-bg); color: var(--mcv-red);}

    .mcv-candidate-top {
        display: flex; align-items: center; gap: 12px; margin-bottom: .3rem;
    }
    .mcv-avatar {
        width: 38px; height: 38px; border-radius: 50%; flex-shrink: 0;
        background: var(--mcv-primary-bg); color: var(--mcv-primary-dark);
        font-weight: 700; font-size: .85rem; display: flex; align-items: center; justify-content: center;
    }
    .mcv-candidate-name {font-weight: 700; font-size: 1.02rem; color: var(--mcv-ink);}

    .mcv-qa-box {
        background: var(--mcv-primary-bg); border-left: 4px solid var(--mcv-primary);
        border-radius: 0 12px 12px 0; padding: .8rem 1rem; margin-top: .5rem; font-size: .93rem;
    }

    div[data-testid="stMetric"] {border: 1px solid var(--mcv-border); padding: 12px; border-radius: 14px; background: #fff;}
    section[data-testid="stSidebar"] {border-right: 1px solid var(--mcv-border);}
    section[data-testid="stSidebar"] .stRadio label p {font-size: .95rem; font-weight: 500;}
</style>
""", unsafe_allow_html=True)


def recommendation_meta(rec: str):
    return {
        "ENTRETIEN": ("entretien", "🟢"),
        "À QUALIFIER": ("qualifier", "🟠"),
        "FAIBLE MATCHING": ("faible", "🔴"),
    }.get(rec, ("qualifier", "⚪"))


def pill(rec: str) -> str:
    css_class, dot = recommendation_meta(rec)
    return f'<span class="mcv-pill {css_class}">{dot} {rec}</span>'


def avatar_initials(filename: str) -> str:
    base = Path(filename).stem.replace("_", " ").replace("-", " ").strip()
    parts = [p for p in base.split() if p]
    if not parts:
        return "CV"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[1][0]).upper()


status_class = "on" if LLM_AVAILABLE else "off"
status_text = "🟢 LLM connecté" if LLM_AVAILABLE else "⚪ Mode déterministe"
st.markdown(f"""
<div class="mcv-header">
  <div class="mcv-logo">MC</div>
  <div>
    <h1>{APP_NAME}</h1>
    <p>Matching intelligent de CV IT — classement, preuves, compétences, questions d'entretien</p>
  </div>
  <div class="mcv-status {status_class}">{status_text}</div>
</div>
""", unsafe_allow_html=True)

# ----------------------------- Sidebar -----------------------------
with st.sidebar:
    st.markdown(
        '<div style="display:flex;align-items:center;gap:8px;margin-bottom:1rem;">'
        '<div class="mcv-logo" style="width:32px;height:32px;font-size:.75rem;">MC</div>'
        f'<span style="font-weight:700;">{APP_NAME}</span></div>',
        unsafe_allow_html=True,
    )
    mode = st.radio("Mode", ["Démo", "Analyser des CV"], index=0 if st.session_state.mode == "Démo" else 1, key="mode_selector")
    if mode != st.session_state.mode:
        st.session_state.mode = mode
        st.rerun()
    st.divider()
    if LLM_AVAILABLE:
        st.success("LLM connecté")
    else:
        st.info("Mode déterministe · LLM optionnel")
    st.caption("Les données de session sont conservées lorsque vous changez de mode.")
    st.divider()
    st.caption("Rien n'est stocké de façon permanente : les CV restent en mémoire le temps de la session uniquement.")
    if st.button("🗑️ Effacer les données de cette session", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# ----------------------------- DEMO -----------------------------
if mode == "Démo":
    st.subheader("🚀 Démonstration")
    st.info("Cette démo montre le principe de MatchingCVIT : distinguer une compétence simplement déclarée d'une compétence réellement démontrée par des expériences ou projets.")
    st.text_area("Fiche de poste (démo)", DEMO_JOB_TEXT, height=130, disabled=True, key="demo_job")

    if st.session_state.demo_results is None:
        st.session_state.demo_results = run_demo()
    demo_results = st.session_state.demo_results

    rows = [{
        "Candidat": name, "Matching": scores[0], "Evidence": scores[1],
        "Alertes": len(scores[2]), "Recommandation": scores[4],
    } for name, skills, scores in demo_results]
    st.dataframe(pd.DataFrame(rows).sort_values("Matching", ascending=False), use_container_width=True, hide_index=True)

    for name, skills, scores in demo_results:
        matching, evidence, alerts, questions, recommendation = scores
        header = (f'<div class="mcv-candidate-top"><div class="mcv-avatar">{avatar_initials(name)}</div>'
                  f'<div><div class="mcv-candidate-name">{name}</div>{pill(recommendation)}</div></div>')
        with st.expander(f"{name} — {matching}% / Evidence {evidence}%"):
            st.markdown(header, unsafe_allow_html=True)
            m1, m2 = st.columns(2)
            m1.metric("Matching", f"{matching}%")
            m2.metric("Evidence", f"{evidence}%")
            data = [{
                "Compétence": s.skill,
                "Déclarée": "Oui" if s.declared else "Non",
                "Verdict": VERDICT_LABELS[s.verdict],
                "Confiance": round(s.confidence * 100),
                "Durée (ans)": s.duration_years,
                "Preuve": " | ".join(e.quote for e in best_evidence(s)),
            } for s in skills if s.required or s.preferred]
            st.dataframe(
                pd.DataFrame(data), use_container_width=True, hide_index=True,
                column_config={"Confiance": st.column_config.ProgressColumn(
                    "Confiance", format="%d%%", min_value=0, max_value=100)},
            )
            if alerts:
                st.markdown("**Alertes**")
                for a in alerts:
                    st.warning(a, icon="⚠️")
            if questions:
                st.markdown("**Questions d'entretien ciblées**")
                for q in questions:
                    st.write("•", q)
            skill_names = [s.skill for s in skills]
            if skill_names:
                chosen = st.selectbox("Poser une question de preuve", skill_names, key=f"qa_demo_{name}")
                target = next(s for s in skills if s.skill == chosen)
                st.markdown(
                    f'<div class="mcv-qa-box"><b>Le candidat a-t-il réellement utilisé {chosen} ?</b><br>'
                    f'{ask_about_skill(target, use_llm=LLM_AVAILABLE).replace(chr(10), "<br>")}</div>',
                    unsafe_allow_html=True,
                )

    if st.session_state.last_output:
        st.success("Une analyse réelle existe aussi dans cette session. Elle sera conservée si vous revenez au mode « Analyser des CV ». ")

# ----------------------------- ANALYSE REELLE -----------------------------
else:
    st.subheader("1. 🎯 Définir le besoin")
    job_text = st.text_area(
        "Fiche de poste",
        value=st.session_state.job_text,
        height=180,
        placeholder="Exemple : Développeur Full Stack Java/Angular, 3 ans d'expérience minimum...",
        key="job_text_area",
    )
    st.session_state.job_text = job_text

    job = parse_job_description(job_text) if job_text else None
    detected_required = job.required_skills if job else []
    detected_preferred = job.preferred_skills if job else []

    if job:
        st.caption(
            f"Détecté automatiquement · Requises : {', '.join(detected_required) or '—'} · "
            f"Souhaitées : {', '.join(detected_preferred) or '—'} · "
            f"Ancienneté min. : {job.min_years_experience or '—'} an(s) · Niveau : {job.seniority or '—'}"
        )

    # Ajout manuel d'une compétence : elle devient disponible partout dans la session.
    with st.expander("➕ Ajouter manuellement une compétence / technologie"):
        col1, col2 = st.columns([3, 1])
        with col1:
            custom = st.text_input("Nom de la compétence", placeholder="Ex. OpenShift, SAP S/4HANA, ServiceNow...", key="custom_skill_input")
        with col2:
            st.write("")
            st.write("")
            add_clicked = st.button("Ajouter", use_container_width=True)
        if add_clicked:
            if add_custom_skill(custom):
                st.success(f"« {custom.strip()} » a été ajoutée à la bibliothèque de compétences de la session.")
                st.rerun()
            elif custom.strip() in SKILLS:
                st.info("Cette compétence existe déjà.")
            else:
                st.warning("Saisissez un nom de compétence.")

    options = sorted(set(all_skill_names()) | set(detected_required) | set(detected_preferred))

    # Dès que la fiche de poste change, les champs sont alimentés directement
    # par l'analyse automatique. Ensuite, les choix manuels de l'utilisateur
    # restent persistants pendant les reruns et les changements de mode.
    if st.session_state.get("last_parsed_job_text") != job_text:
        st.session_state.required = [x for x in detected_required if x in options]
        st.session_state.preferred = [x for x in detected_preferred if x in options]
        st.session_state.last_parsed_job_text = job_text
        # Les widgets utilisent leur propre état : on le synchronise avant
        # leur création afin que les compétences détectées apparaissent bien
        # dans les sélecteurs, et pas uniquement dans les suggestions.
        st.session_state.required_selector = st.session_state.required
        st.session_state.preferred_selector = st.session_state.preferred

    c1, c2 = st.columns(2)
    with c1:
        required = st.multiselect(
            "🔴 Compétences obligatoires",
            options,
            key="required_selector",
            help="Détection automatique depuis la fiche de poste + sélection manuelle.",
        )
    with c2:
        preferred = st.multiselect(
            "🟢 Technologies / compétences souhaitées",
            options,
            key="preferred_selector",
            help="Détection automatique depuis la fiche de poste + sélection manuelle. Les souhaitées ne sont pas bloquantes.",
        )
    st.session_state.required = required
    st.session_state.preferred = preferred

    if job:
        st.success(
            f"Détection automatique appliquée : {len(detected_required)} obligatoire(s) · "
            f"{len(detected_preferred)} souhaitée(s)."
        )

    st.subheader("2. 📄 Charger les CV")
    uploads = st.file_uploader(
        "Déposez les CV (PDF, DOCX, TXT)",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        key="cv_uploader",
    )
    if uploads:
        st.session_state.candidate_files = [(u.name, bytes(u.getbuffer())) for u in uploads]
    elif st.session_state.candidate_files:
        st.caption(f"{len(st.session_state.candidate_files)} CV déjà conservé(s) dans la session.")

    action_col1, action_col2 = st.columns([1, 4])
    with action_col1:
        analyze_clicked = st.button("🚀 Analyser les CV", type="primary", use_container_width=True)
    with action_col2:
        if st.session_state.last_output:
            st.caption("Le dernier classement reste disponible tant qu'il n'est pas remplacé par une nouvelle analyse.")

    if analyze_clicked:
        candidate_files = st.session_state.candidate_files
        if not job_text or not candidate_files or not required:
            st.warning("Ajoutez une fiche de poste, au moins un CV et une ou plusieurs compétences obligatoires.")
        else:
            output = []
            progress = st.progress(0, text="Analyse des CV...")
            for i, (filename, file_bytes) in enumerate(candidate_files):
                suffix = Path(filename).suffix
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
                    f.write(file_bytes)
                    temp_path = f.name
                try:
                    text = extract_text(temp_path)
                    blocks = extract_experience_blocks(text)
                    skills = analyze_skills(text)
                    years = total_years_experience(blocks)
                    matching, evidence, alerts, questions, recommendation = score_candidate(
                        skills, required, preferred,
                        min_years_experience=job.min_years_experience if job else None,
                        candidate_years=years,
                        skill_weights=job.skill_weights if job else None,
                        consistency_alerts=chronology_alerts(blocks),
                    )
                    output.append({
                        "name": filename,
                        "matching": matching,
                        "evidence": evidence,
                        "recommendation": recommendation,
                        "alerts": alerts,
                        "questions": questions,
                        "skills": skills,
                        "file_bytes": file_bytes,
                    })
                finally:
                    try:
                        Path(temp_path).unlink(missing_ok=True)
                    except Exception:
                        pass
                progress.progress((i + 1) / len(candidate_files), text=f"Analyse : {filename}")
            progress.empty()
            st.session_state.last_output = output
            st.success(f"Analyse terminée : {len(output)} candidat(s) classé(s).")

    output = st.session_state.last_output
    if output:
        st.subheader("3. 🏆 Classement recruteur")
        ranked = sorted(output, key=lambda x: x["matching"], reverse=True)
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Candidats analysés", len(ranked))
        with m2:
            st.metric("Meilleur matching", f"{ranked[0]['matching']}%" if ranked else "—")
        with m3:
            st.metric("Score moyen", f"{sum(x['matching'] for x in ranked)/len(ranked):.1f}%" if ranked else "—")

        table = pd.DataFrame([
            {"Rang": i + 1, "Candidat": x["name"], "Matching": x["matching"], "Evidence": x["evidence"],
             "Recommandation": x["recommendation"], "Alertes": len(x["alerts"])}
            for i, x in enumerate(ranked)
        ])
        st.dataframe(
            table, use_container_width=True, hide_index=True,
            column_config={
                "Matching": st.column_config.ProgressColumn("Matching", format="%d%%", min_value=0, max_value=100),
                "Evidence": st.column_config.ProgressColumn("Evidence", format="%d%%", min_value=0, max_value=100),
            },
        )

        # Export Excel dans un fichier temporaire compatible Windows/Linux.
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            excel_path = tmp.name
        try:
            export_to_excel([
                (x["name"], x["matching"], x["evidence"], x["recommendation"], x["alerts"], x["questions"], x["skills"])
                for x in ranked
            ], excel_path)
            with open(excel_path, "rb") as f:
                st.download_button("📥 Exporter le classement Excel", f.read(), file_name="MatchingCVIT_classement.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        finally:
            Path(excel_path).unlink(missing_ok=True)

        st.subheader("4. 👤 Détail par candidat")
        for rank, candidate in enumerate(ranked, start=1):
            name = candidate["name"]
            matching = candidate["matching"]
            evidence = candidate["evidence"]
            recommendation = candidate["recommendation"]
            alerts = candidate["alerts"]
            questions = candidate["questions"]
            skills = candidate["skills"]
            with st.expander(f"#{rank} · {name} — {matching}% / Evidence {evidence}% — {recommendation}", expanded=(rank == 1)):
                header = (f'<div class="mcv-candidate-top"><div class="mcv-avatar">{avatar_initials(name)}</div>'
                          f'<div><div class="mcv-candidate-name">{name}</div>{pill(recommendation)}</div></div>')
                st.markdown(header, unsafe_allow_html=True)
                top1, top2, top3 = st.columns([1, 1, 1.4])
                with top1:
                    st.metric("Matching", f"{matching}%")
                with top2:
                    st.metric("Evidence", f"{evidence}%")
                with top3:
                    st.download_button(
                        "📄 Télécharger le CV",
                        data=candidate["file_bytes"],
                        file_name=name,
                        mime="application/pdf" if name.lower().endswith(".pdf") else ("application/vnd.openxmlformats-officedocument.wordprocessingml.document" if name.lower().endswith(".docx") else "text/plain"),
                        key=f"download_cv_{rank}_{name}",
                        use_container_width=True,
                    )

                rows = [{
                    "Compétence": s.skill,
                    "Type": "Requise" if s.required else ("Souhaitée" if s.preferred else "Autre"),
                    "Déclarée": "Oui" if s.declared else "Non",
                    "Verdict": VERDICT_LABELS[s.verdict],
                    "Confiance": round(s.confidence * 100),
                    "Durée (ans)": s.duration_years,
                    "Preuve": " | ".join(e.quote for e in best_evidence(s)),
                } for s in skills if s.required or s.preferred or s.declared]
                st.dataframe(
                    pd.DataFrame(rows), use_container_width=True, hide_index=True,
                    column_config={"Confiance": st.column_config.ProgressColumn(
                        "Confiance", format="%d%%", min_value=0, max_value=100)},
                )

                if alerts:
                    st.markdown("**⚠️ Alertes**")
                    for a in alerts:
                        st.warning(a, icon="⚠️")
                if questions:
                    st.markdown("**💬 Questions d'entretien ciblées**")
                    for q in questions:
                        st.write("•", q)

                st.markdown("**🔍 Poser une question de preuve**")
                skill_names = [s.skill for s in skills]
                if skill_names:
                    chosen = st.selectbox("Compétence", skill_names, key=f"qa_real_{rank}_{name}")
                    target = next(s for s in skills if s.skill == chosen)
                    answer = ask_about_skill(target, use_llm=LLM_AVAILABLE).replace(chr(10), "<br>")
                    st.markdown(
                        f'<div class="mcv-qa-box"><b>Le candidat a-t-il réellement utilisé {chosen} '
                        f'en contexte professionnel ?</b><br>{answer}</div>',
                        unsafe_allow_html=True,
                    )

        st.divider()
        st.caption("MatchingCVIT · Les résultats constituent une aide au recrutement et doivent être validés par un entretien humain.")
