from src.config import *

def calculate_trajectory_scores(candidate):

    career = candidate.get("career_history", [])
    summary = candidate.get("profile", {}).get("summary", "").lower()

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

    all_text = summary + " " + " ".join([j.get("description", "").lower() for j in career])
    
    if any(word in all_text for word in ["github", "open source", "contributed to", "oss"]):
        features["open_source_score"] = 1
    
    eval_keywords = {"ndcg", "map", "mrr", "benchmarking", "a/b testing", "evaluation framework"}
    features["eval_framework_score"] = sum(1 for word in eval_keywords if word in all_text)

    vector_db_keywords = {"faiss", "pinecone", "milvus", "qdrant", "weaviate", "opensearch", "elasticsearch"}

    features["vector_db_deployments"] = len([word for word in vector_db_keywords if word in all_text])

    for role_data in career:
        months = role_data.get("duration_months", 0)
        desc = role_data.get("description", "").lower()
        company = role_data.get("company", "").lower()
        title = role_data.get("title", "").lower()

        if any(c in company for c in CONSULTING_FIRMS):
            features["consulting_years"] += months

        else:
            features["product_company_years"] += months

        if any(word in title for word in ["manager", "head", "director", "vp"]):
            features["manager_years"] += months

        if any(word in desc for word in PRODUCTION_KEYWORDS):
            features["production_ml_years"] += months

        search_rec_keywords = {"search", "recommendation", "retrieval", "information retrieval", "recsys"}
        if any(word in desc for word in search_rec_keywords):
            features["search_rec_years"] += months

        if any(word in desc for word in ["ranking", "learning to rank", "ltr", "reranking"]):
            features["ranking_years"] += months

        if any(word in desc for word in ["nlp", "transformer", "llm", "bert", "gpt", "language model"]):
            features["nlp_years"] += months

        if any(word in desc for word in RESEARCH_KEYWORDS):
            features["research_years"] += months

    for key in features:
        if "years" in key:
            features[key] = round(features[key] / 12, 2)

    return features
