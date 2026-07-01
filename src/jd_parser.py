from .config import (
    PRODUCTION_KEYWORDS,
    RESEARCH_KEYWORDS,
    CONSULTING_FIRMS,
)

import re


# ----------------------------
# Keyword Libraries
# ----------------------------

SKILLS = [
    "python",
    "retrieval",
    "ranking",
    "semantic search",
    "dense retrieval",
    "hybrid retrieval",
    "candidate matching",
    "recommendation systems",
    "embeddings",
    "sentence-transformers",
    "rag",
]

VECTOR_DBS = [
    "faiss",
    "pinecone",
    "milvus",
    "qdrant",
    "weaviate",
    "opensearch",
    "elasticsearch",
]

LLM_SKILLS = [
    "lora",
    "qlora",
    "peft",
    "fine-tuning",
    "llamaindex",
    "langchain",
]

EVAL_FRAMEWORKS = [
    "ndcg",
    "map",
    "mrr",
    "offline benchmarking",
    "a/b testing",
]

RESPONSIBILITY_KEYWORDS = [
    "retrieval",
    "ranking",
    "recommendation",
    "candidate matching",
    "semantic search",
    "production",
    "deployment",
    "evaluation",
]

EDUCATION = [
    "b.tech",
    "b.e",
    "bachelor",
    "master",
    "m.tech",
    "m.e",
    "phd",
]

SENIORITY = [
    "intern",
    "junior",
    "engineer",
    "senior",
    "staff",
    "lead",
    "principal",
    "architect",
]

LOCATIONS = [
    "pune",
    "noida",
    "hyderabad",
    "mumbai",
    "bangalore",
    "bengaluru",
    "delhi",
    "chennai",
    "india",
]


# ----------------------------
# Helpers
# ----------------------------

def extract_section(text, start, end_keywords):
    start_idx = text.find(start)

    if start_idx == -1:
        return ""

    end_idx = len(text)

    for word in end_keywords:
        pos = text.find(word, start_idx + len(start))
        if pos != -1:
            end_idx = min(end_idx, pos)

    return text[start_idx:end_idx]


# ----------------------------
# Main Parser
# ----------------------------

def parse_dynamic_jd(jd_text):

    text = jd_text.lower()

    required_section = extract_section(
        text,
        "required",
        ["preferred", "preferred candidate", "avoid"],
    )

    preferred_section = extract_section(
        text,
        "preferred skills",
        ["preferred candidate", "avoid"],
    )

    candidate_section = extract_section(
        text,
        "preferred candidate",
        ["avoid"],
    )

    avoid_section = extract_section(
        text,
        "avoid",
        [],
    )

    # ---------------- Skills ----------------

    required_skills = [
        k for k in SKILLS + VECTOR_DBS + EVAL_FRAMEWORKS
        if k in required_section
    ]

    preferred_skills = [
        k for k in LLM_SKILLS + SKILLS
        if k in preferred_section
    ]

    # ---------------- Responsibilities ----------------

    responsibilities = [
        r for r in RESPONSIBILITY_KEYWORDS
        if r in text
    ]

    # ---------------- Locations ----------------

    locations = [
        l for l in LOCATIONS
        if l in text
    ]

    if not locations:
        locations = ["india"]

    # ---------------- Experience ----------------



    min_exp = 0
    max_exp = None

 
    range_match = re.search(
        r'(\d+)\s*(?:-|–|—|to)\s*(\d+)\s*\+?\s*years',
        text
    )

    if range_match:
        min_exp = int(range_match.group(1))
        max_exp = int(range_match.group(2))

    else:

        single_match = re.search(
            r'(\d+)\s*\+?\s*years',
            text
        )

        if single_match:
            min_exp = int(single_match.group(1))
        

    # ---------------- Seniority ----------------

    seniority = None

    for s in SENIORITY:
        if s in text:
            seniority = s
            break

    # ---------------- Education ----------------

    education = [
        e for e in EDUCATION
        if e in text
    ]

    # ---------------- Evaluation ----------------

    evaluation = [
        e for e in EVAL_FRAMEWORKS
        if e in text
    ]

    # ---------------- Vector DB ----------------

    vector_dbs = [
        v for v in VECTOR_DBS
        if v in text
    ]

    # ---------------- System Engineering ----------------

    from .config import SYSTEM_KEYWORDS

    system_keywords = [
        s for s in SYSTEM_KEYWORDS
        if s in text
    ]

    # ---------------- LLM ----------------

    llm = [
        l for l in LLM_SKILLS
        if l in text
    ]

    # ---------------- Production ----------------

    production_required = any(
        word in text
        for word in [
            "production",
            "deployed",
            "deployment",
            "shipped",
            "real users",
        ]
    )

    # ---------------- Research ----------------

    research_friendly = any(
        word in text
        for word in RESEARCH_KEYWORDS
    )

    # ---------------- Disqualifiers ----------------

    disqualifiers = []

    if "consulting" in avoid_section:
        disqualifiers.extend(list(CONSULTING_FIRMS))

    if "research" in avoid_section:
        disqualifiers.append("pure_research")

    if "langchain" in avoid_section:
        disqualifiers.append("langchain_demo")

    if "computer vision" in avoid_section:
        disqualifiers.append("computer_vision")

    if "robotics" in avoid_section:
        disqualifiers.append("robotics")

    if "speech" in avoid_section:
        disqualifiers.append("speech")

    # ---------------- Preferred Candidate ----------------

    preferred_candidate = []

    if "product-company" in candidate_section:
        preferred_candidate.append("product_company")

    if "recruiter engagement" in candidate_section:
        preferred_candidate.append("high_recruiter_engagement")

    if "short notice" in candidate_section:
        preferred_candidate.append("short_notice")

    if "production code" in candidate_section:
        preferred_candidate.append("recent_production")

    # ---------------- Return ----------------

    return {
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "responsibilities": responsibilities,
        "preferred_candidate": preferred_candidate,
        "vector_databases": vector_dbs,
        "system_keywords": system_keywords,
        "evaluation_frameworks": evaluation,
        "llm_skills": llm,
        "education": education,
        "seniority": seniority,
        "target_locations": locations,
        "min_yoe": min_exp,
        "max_yoe": max_exp,
        "production_required": production_required,
        "research_friendly": research_friendly,
        "disqualifiers": disqualifiers,
        "production_signals": PRODUCTION_KEYWORDS,
        "research_signals": RESEARCH_KEYWORDS,
        "full_text": text,
    }


def get_jd_cont(jd_text=None):
    if jd_text:
        return parse_dynamic_jd(jd_text)

    from .config import TARGET_JD
    return parse_dynamic_jd(TARGET_JD)