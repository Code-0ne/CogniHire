from .config import PRODUCTION_KEYWORDS, RESEARCH_KEYWORDS, CONSULTING_FIRMS

JD_req = {
    "must_have" : [ 
        "embeddings", "vector database", "retrieval", "ranking", 
        "python", "ndcg", "mrr", "map", "evaluation framework", 
        "sentence-transformers", "faiss", "pinecone", "milvus", "qdrant"
    ],
    "nice_to_have" : ["lora", "qlora", "peft", "fine-tuning", "learning to rank", 
        "xgboost", "distributed systems", "inference optimization"
    ],
        "disqualifiers": {
        "pure_consulting": CONSULTING_FIRMS,
        "pure_research": ["academic lab", "research only", "theoretical"],
        "non_coder_titles": ["manager", "director", "vp", "architect", "lead"] 
    },
    "production_signals": PRODUCTION_KEYWORDS,
    "research_signals": RESEARCH_KEYWORDS,
    "target_locations": ["pune", "noida", "hyderabad", "mumbai", "delhi", "india"]
}

def get_jd_cont():
    return JD_req