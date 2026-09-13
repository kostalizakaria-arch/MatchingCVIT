# Dictionnaire de compétences IT : alias multiples + versions + catégorie.
# Le dictionnaire peut être enrichi à chaud depuis l'interface.

SKILLS = {
    # Langages
    "Java": {"aliases": ["java 8", "java 11", "java 17", "java 21", "java"], "category": "Langage"},
    "Python": {"aliases": ["python3", "python 3", "python"], "category": "Langage"},
    "JavaScript": {"aliases": ["javascript", "js es6", "js"], "category": "Langage"},
    "TypeScript": {"aliases": ["typescript", "ts"], "category": "Langage"},
    "PHP": {"aliases": ["php7", "php8", "php"], "category": "Langage"},
    "C#": {"aliases": ["c#", "csharp"], "category": "Langage"},
    "C++": {"aliases": ["c++", "cpp"], "category": "Langage"},
    "C": {"aliases": ["langage c", " c ", "c programming"], "category": "Langage"},
    "Go": {"aliases": ["golang", "go language"], "category": "Langage"},
    "Ruby": {"aliases": ["ruby"], "category": "Langage"},
    "Kotlin": {"aliases": ["kotlin"], "category": "Langage"},
    "Swift": {"aliases": ["swift"], "category": "Langage"},
    "Dart": {"aliases": ["dart"], "category": "Langage"},
    "Scala": {"aliases": ["scala"], "category": "Langage"},
    "R": {"aliases": ["r language", "r programming"], "category": "Langage"},
    "Shell/Bash": {"aliases": ["bash", "shell script", "shell scripting"], "category": "Langage"},

    # Frameworks / runtime
    "Spring Boot": {"aliases": ["spring boot", "springboot"], "category": "Framework"},
    "Spring": {"aliases": ["spring framework", "spring"], "category": "Framework"},
    "Angular": {"aliases": ["angular 2", "angularjs", "angular"], "category": "Framework"},
    "React": {"aliases": ["react.js", "reactjs", "react"], "category": "Framework"},
    "Vue.js": {"aliases": ["vue.js", "vuejs", "vue"], "category": "Framework"},
    "Node.js": {"aliases": ["node.js", "nodejs", "node"], "category": "Runtime"},
    "Django": {"aliases": ["django"], "category": "Framework"},
    "Flask": {"aliases": ["flask"], "category": "Framework"},
    "FastAPI": {"aliases": ["fastapi", "fast api"], "category": "Framework"},
    "Symfony": {"aliases": ["symfony"], "category": "Framework"},
    "Laravel": {"aliases": ["laravel"], "category": "Framework"},
    ".NET": {"aliases": [".net", "dotnet", "asp.net", "asp net"], "category": "Framework"},
    "ASP.NET Core": {"aliases": ["asp.net core", "asp net core"], "category": "Framework"},
    "Flutter": {"aliases": ["flutter"], "category": "Framework mobile"},
    "React Native": {"aliases": ["react native"], "category": "Framework mobile"},

    # API / architecture
    "REST API": {"aliases": ["rest api", "restful", "api rest", "api restful"], "category": "Architecture"},
    "GraphQL": {"aliases": ["graphql"], "category": "Architecture"},
    "Microservices": {"aliases": ["microservices", "micro-services"], "category": "Architecture"},
    "API Gateway": {"aliases": ["api gateway"], "category": "Architecture"},
    "WebSockets": {"aliases": ["websocket", "websockets"], "category": "Architecture"},

    # Bases de données
    "SQL": {"aliases": ["sql"], "category": "Base de données"},
    "PostgreSQL": {"aliases": ["postgresql", "postgres", "psql"], "category": "Base de données"},
    "MySQL": {"aliases": ["mysql", "mariadb"], "category": "Base de données"},
    "Oracle": {"aliases": ["oracle db", "oracle sql", "oracle"], "category": "Base de données"},
    "SQL Server": {"aliases": ["sql server", "mssql", "t-sql"], "category": "Base de données"},
    "MongoDB": {"aliases": ["mongodb", "mongo"], "category": "Base de données"},
    "Redis": {"aliases": ["redis"], "category": "Base de données"},
    "Cassandra": {"aliases": ["cassandra", "apache cassandra"], "category": "Base de données"},
    "MariaDB": {"aliases": ["mariadb"], "category": "Base de données"},
    "Elasticsearch": {"aliases": ["elasticsearch", "elastic search"], "category": "Data"},

    # Cloud / DevOps
    "AWS": {"aliases": ["aws", "amazon web services"], "category": "Cloud"},
    "Azure": {"aliases": ["azure", "microsoft azure"], "category": "Cloud"},
    "GCP": {"aliases": ["gcp", "google cloud", "google cloud platform"], "category": "Cloud"},
    "Docker": {"aliases": ["docker", "containerisation", "containerization"], "category": "DevOps"},
    "Kubernetes": {"aliases": ["kubernetes", "k8s"], "category": "DevOps"},
    "Jenkins": {"aliases": ["jenkins"], "category": "DevOps"},
    "GitLab CI/CD": {"aliases": ["gitlab ci", "gitlab ci/cd", "gitlab pipeline"], "category": "DevOps"},
    "CI/CD": {"aliases": ["ci/cd", "intégration continue", "integration continue", "déploiement continu", "deployment continuous"], "category": "DevOps"},
    "Terraform": {"aliases": ["terraform"], "category": "DevOps"},
    "Ansible": {"aliases": ["ansible"], "category": "DevOps"},
    "OpenShift": {"aliases": ["openshift", "red hat openshift"], "category": "DevOps"},
    "Helm": {"aliases": ["helm chart", "helm"], "category": "DevOps"},
    "Argo CD": {"aliases": ["argo cd", "argocd"], "category": "DevOps"},
    "Git": {"aliases": ["git"], "category": "Outils"},
    "GitHub": {"aliases": ["github"], "category": "Outils"},
    "GitLab": {"aliases": ["gitlab"], "category": "Outils"},
    "Bitbucket": {"aliases": ["bitbucket"], "category": "Outils"},

    # Data / BI / messaging / ETL
    "Informatica": {"aliases": ["informatica", "informatica cloud", "informatica powercenter"], "category": "ETL"},
    "Talend": {"aliases": ["talend"], "category": "ETL"},
    "Power BI": {"aliases": ["power bi", "powerbi"], "category": "Data/BI"},
    "Tableau": {"aliases": ["tableau"], "category": "Data/BI"},
    "Kafka": {"aliases": ["kafka", "apache kafka"], "category": "Data"},
    "Spark": {"aliases": ["spark", "apache spark", "pyspark"], "category": "Data"},
    "Hadoop": {"aliases": ["hadoop", "apache hadoop"], "category": "Data"},
    "Databricks": {"aliases": ["databricks"], "category": "Data"},
    "Airflow": {"aliases": ["airflow", "apache airflow"], "category": "Data"},
    "RabbitMQ": {"aliases": ["rabbitmq", "rabbit mq"], "category": "Messaging"},

    # Systèmes / virtualisation / réseaux
    "Linux": {"aliases": ["linux", "ubuntu", "red hat linux", "rhel", "debian"], "category": "Système"},
    "Windows Server": {"aliases": ["windows server", "windows serveur"], "category": "Système"},
    "Unix": {"aliases": ["unix", "aix", "solaris"], "category": "Système"},
    "VMware": {"aliases": ["vmware", "vsphere", "vcenter"], "category": "Virtualisation"},
    "TCP/IP": {"aliases": ["tcp/ip", "tcp ip"], "category": "Réseaux"},
    "DNS": {"aliases": ["dns"], "category": "Réseaux"},
    "DHCP": {"aliases": ["dhcp"], "category": "Réseaux"},
    "VLAN": {"aliases": ["vlan", "802.1q"], "category": "Réseaux"},
    "VPN": {"aliases": ["vpn", "ipsec vpn", "ssl vpn"], "category": "Réseaux"},
    "Cisco": {"aliases": ["cisco", "ccna", "ios cisco"], "category": "Réseaux"},
    "Fortinet": {"aliases": ["fortinet", "fortigate"], "category": "Réseaux/Sécurité"},
    "Load Balancing": {"aliases": ["load balancing", "load balancer", "équilibrage de charge"], "category": "Réseaux"},

    # Sécurité / qualité / gestion
    "Cybersécurité": {"aliases": ["cybersécurité", "cybersecurity", "sécurité informatique", "information security"], "category": "Sécurité"},
    "SIEM": {"aliases": ["siem", "security information and event management"], "category": "Sécurité"},
    "IAM": {"aliases": ["iam", "identity and access management"], "category": "Sécurité"},
    "Firewall": {"aliases": ["firewall", "pare-feu", "pare feu"], "category": "Sécurité"},
    "EDR": {"aliases": ["edr", "endpoint detection and response"], "category": "Sécurité"},
    "Pentest": {"aliases": ["pentest", "penetration test", "tests d'intrusion"], "category": "Sécurité"},
    "JUnit": {"aliases": ["junit", "tests unitaires"], "category": "Qualité"},
    "Selenium": {"aliases": ["selenium"], "category": "Qualité"},
    "SonarQube": {"aliases": ["sonarqube", "sonar"], "category": "Qualité"},
    "Agile/Scrum": {"aliases": ["agile", "scrum", "kanban", "sprint"], "category": "Méthodologie"},
    "ITIL": {"aliases": ["itil"], "category": "Méthodologie"},
    "Jira": {"aliases": ["jira"], "category": "Gestion de projet"},
    "Confluence": {"aliases": ["confluence"], "category": "Gestion de projet"},
    "SAP": {"aliases": ["sap", "sap erp"], "category": "ERP"},
    "Salesforce": {"aliases": ["salesforce"], "category": "CRM"},
}


def find_declared_skills(text: str):
    low = text.lower()
    return {skill: any(alias.lower() in low for alias in data["aliases"]) for skill, data in SKILLS.items()}


def skill_aliases(skill: str):
    return SKILLS[skill]["aliases"]


def all_skill_names():
    return list(SKILLS.keys())


def add_custom_skill(name: str, aliases=None, category="Compétence personnalisée"):
    name = " ".join((name or "").strip().split())
    if not name:
        return False
    if name not in SKILLS:
        aliases = aliases or [name]
        SKILLS[name] = {"aliases": list(dict.fromkeys([name] + aliases)), "category": category}
        return True
    return False
