# MatchingCVIT

Matching intelligent de CV IT : Evidence Engine, extraction automatique de
fiche de poste, scoring pondéré, export Excel, et un moteur de questions/
réponses qui justifie chaque verdict par des citations du CV.

## Cette version

- **Bibliothèque de compétences élargie** (~80 technologies) : langages,
  frameworks, bases de données, cloud, DevOps, réseaux, sécurité, ERP,
  gestion de projet — `app/skills.py`.
- **Détection de fiche de poste plus fine** : reconnaît les titres de
  section (« Compétences obligatoires », « Compétences souhaitées »),
  évite les faux positifs (ex : ne confond pas « Go » avec « Google »),
  et ignore les compétences génériques déjà couvertes par une plus
  précise (ex : ne remonte pas « SQL » si « SQL Server » est détecté) —
  `app/job_parser.py`.
- **Ajout manuel de compétences** absentes du dictionnaire, utilisables
  immédiatement dans l'analyse.
- **Aucune perte de données en changeant de mode** : la fiche de poste,
  les CV déposés et le dernier classement restent en mémoire tant que la
  page n'est pas rechargée.
- **Téléchargement du CV original** de chaque candidat depuis son
  détail, export du classement complet en Excel.
- **Interface repensée** : en-tête avec indicateur de statut LLM, cartes
  candidat avec avatar et badge de recommandation coloré (🟢 Entretien /
  🟠 À qualifier / 🔴 Faible matching), barres de confiance visuelles
  dans les tableaux de compétences (`st.column_config.ProgressColumn`).

## Démarrage local

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt
streamlit run streamlit_app.py
```

Le mode **Démo** fonctionne sans rien configurer. Pour activer la
reformulation IA des réponses et l'extraction LLM des expériences :

```bash
export ANTHROPIC_API_KEY="votre_clé"
```

Sans clé, l'application reste pleinement fonctionnelle (moteur
déterministe).

## Important : nom de l'application, pas nom de domaine

Le titre de la page et l'onglet du navigateur affichent bien
**« MatchingCVIT »**. En revanche, l'application tourne en local sur
votre PC (`http://localhost:8501`) — elle n'est pas publiée sur un vrai
nom de domaine internet accessible depuis l'extérieur. Cela nécessiterait
un hébergement séparé (Streamlit Community Cloud, un serveur, etc.), une
étape distincte de ce que ce paquet fournit.

## Confidentialité des CV

Aucun CV n'est stocké de façon permanente : les fichiers restent en
mémoire de session (RAM) le temps de l'analyse, un fichier temporaire
est supprimé aussitôt l'extraction terminée, et tout est effacé à la
fermeture de l'onglet ou via le bouton **« 🗑️ Effacer les données de
cette session »** dans la barre latérale.

## Ce que le système ne fait toujours pas

L'outil ne conclut jamais qu'un candidat ment. Il produit des signaux
(🟢 CONFIRMÉ / 🟡 PROBABLE / 🟠 À VÉRIFIER / 🔴 NON DÉMONTRÉ) avec les
citations correspondantes. **La décision finale reste humaine.**
