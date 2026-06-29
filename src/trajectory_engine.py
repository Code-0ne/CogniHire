# src/trajectory_engine.py
from src.config import *

def calculate_trajectory_scores(candidate):
    """
    Analyzes the career trajectory of a candidate to derive structured 
    experience features based on duration and keyword analysis.
    """
    career = candidate.get("career_history", [])
    summary = candidate.get("profile", {}).get("summary", "").lower()
    
    # Feature Map: stores total months for each category
    features = {
        "product_company_years": 0,
        "production_ml_years": 0,
        "search_rec_years": 0,
        "ranking_years": 0,
        "nlp_years": 0,
        "research_years": 0,
        "consulting_years": 0,
        "manager_years": 0,
        "open_source_score": 0,
        "eval_framework_score": 0,
        "vector_db_deployments": 0
    }

    # Combine all text for global signals (like open source or eval frameworks)
    all_text = summary + " " + " ".join([j.get("description", "").lower() for j in career])
    
    # 1. Global-level Binary/Count Features
    if any(word in all_text for word in ["github", "open source", "contributed to", "oss"]):
        features["open_source_score"] = 1
    
    eval_keywords = {"ndcg", "map", "mrr", "benchmarking", "a/b testing", "evaluation framework"}
    features["eval_framework_score"] = sum(1 for word in eval_keywords if word in all_text)

    vector_db_keywords = {"faiss", "pinecone", "milvus", "qdrant", "weaviate", "opensearch", "elasticsearch"}
    # Fix: Count unique technologies instead of raw occurrences
    features["vector_db_deployments"] = len([word for word in vector_db_keywords if word in all_text])

    # 2. Temporal-level Features (Analyzing each role)
    for role_data in career:
        months = role_data.get("duration_months", 0)
        desc = role_data.get("description", "").lower()
        company = role_data.get("company", "").lower()
        title = role_data.get("title", "").lower()

        # Consulting Years
        if any(c in company for c in CONSULTING_FIRMS):
            features["consulting_years"] += months

        # Product Company (Inverse of consulting for simplicity)
        else:
            features["product_company_years"] += months

        # Managerial Years
        # Fix: Remove "lead" from management detection as it's common for top individual contributors
        if any(word in title for word in ["manager", "head", "director", "vp"]):
            features["manager_years"] += months

        # Production ML Years
        if any(word in desc for word in PRODUCTION_KEYWORDS):
            features["production_ml_years"] += months

        # Search/Rec Years
        search_rec_keywords = {"search", "recommendation", "retrieval", "information retrieval", "recsys"}
        if any(word in desc for word in search_rec_keywords):
            features["search_rec_years"] += months

        # Ranking Years
        if any(word in desc for word in ["ranking", "learning to rank", "ltr", "reranking"]):
            features["ranking_years"] += months

        # NLP Years
        if any(word in desc for word in ["nlp", "transformer", "llm", "bert", "gpt", "language model"]):
            features["nlp_years"] += months

        # Research Years
        if any(word in desc for word in RESEARCH_KEYWORDS):
            features["research_years"] += months

    # Convert months to years for clarity
    for key in features:
        if "years" in key:
            features[key] = round(features[key] / 12, 2)

    return features
