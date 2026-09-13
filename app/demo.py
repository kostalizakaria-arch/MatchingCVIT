from app.evidence import analyze_skills
from app.scoring import score_candidate
from app.experience_extractor import extract_experience_blocks, total_years_experience, chronology_alerts

DEMO_JOB_TEXT = """
Poste : Développeur Full Stack Java/Angular (confirmé, 3 ans d'expérience minimum)
Compétences requises : Java, Spring Boot, Angular, SQL.
Compétences souhaitées (un plus) : PostgreSQL, REST API, Docker, AWS.
"""

DEMO_JOB = {
    "required": ["Java", "Spring Boot", "Angular", "SQL"],
    "preferred": ["PostgreSQL", "REST API", "Docker", "AWS"],
}

DEMO_CV = {
    "Ahmed": """
COMPETENCES
Java, Spring Boot, Angular, PostgreSQL, Docker, AWS

EXPERIENCE 2022-2025
Développement d'API REST avec Java et Spring Boot.
Développement d'interfaces avec Angular.
Conception de requêtes PostgreSQL.
Utilisation de Docker pour les environnements de développement.

PROJET 2024-2025
Application bancaire : Java 17, Spring Boot, Angular et PostgreSQL.
""",
    "Sara": """
COMPETENCES
Java, Angular, Python, AWS, Docker, Kubernetes

EXPERIENCE 2022-2025
Développement frontend avec Angular.
Intégration d'API REST.
Utilisation de Docker.

PROJET
Application web développée avec Angular et PHP.
""",
}


def run_demo():
    results = []
    for name, text in DEMO_CV.items():
        blocks = extract_experience_blocks(text)
        skills = analyze_skills(text)
        years = total_years_experience(blocks)
        scores = score_candidate(
            skills, DEMO_JOB["required"], DEMO_JOB["preferred"],
            candidate_years=years, consistency_alerts=chronology_alerts(blocks),
        )
        results.append((name, skills, scores))
    return results
