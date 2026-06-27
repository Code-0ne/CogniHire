from .config import PRODUCTION_KEYWORDS, RESEARCH_KEYWORDS, CONSULTING_FIRMS
import re

def parse_dynamic_jd(jd_text):
    """
    Extracts key requirements and constraints from a raw JD text.
    """
    text = jd_text.lower()
    
    # 1. Extract Must-Haves (Keywords associated with 'experience', 'strong', 'required', 'must')
    # We look for common technical terms in the text
    potential_keywords = [
        "embeddings", "vector database", "retrieval", "ranking", "python", 
        "ndcg", "mrr", "map", "evaluation framework", "sentence-transformers", 
        "faiss", "pinecone", "milvus", "qdrant", "pytorch", "tensorflow", "jax"
    ]
    must_have = [k for k in potential_keywords if k in text]
    
    # 2. Extract Locations
    locations = ["pune", "noida", "hyderabad", "mumbai", "delhi", "bangalore", "chennai", "india"]
    target_locations = [loc for loc in locations if loc in text]
    if not target_locations:
        target_locations = ["india"]

    # 3. Extract Experience (e.g., "5+ years", "3-5 years")
    exp_match = re.search(r'(\d+)\+?\s*years', text)
    min_yoe = int(exp_match.group(1)) if exp_match else 0

    return {
        "must_have": must_have,
        "target_locations": target_locations,
        "min_yoe": min_yoe,
        "full_text": text
    }

def get_jd_cont(jd_text=None):
    """
    Returns the JD requirements. If jd_text is provided, it parses it dynamically.
    Otherwise, returns the default static requirements.
    """
    if jd_text:
        return parse_dynamic_jd(jd_text)
    
    # Default static requirements
    return {
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