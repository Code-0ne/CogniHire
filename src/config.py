# Model Configurations
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# Sieve 1: Semantic Recall
TOP_K_RECALL = 3000  # Number of candidates to pull from FAISS

# Sieve 2: Trap & Quality Filters 
MAX_AVG_TENURE_FOR_STABILITY = 1.8  # Years per company (Title-chaser check)
CONSULTING_FIRMS = {
    "tcs", "tata consultancy services", "infosys", "wipro", 
    "accenture", "cognizant", "capgemini", "hcl", "tech mahindra"
}
FRAMEWORK_KEYWORDS = {"langchain", "tutorial", "demo", "wrapper", "api-call"}
SYSTEM_KEYWORDS = {"architecture", "latency", "throughput", "distributed", "index", "optimization"}
WRONG_DOMAIN_KEYWORDS = {"computer vision", "opencv", "robotics", "speech", "audio", "signal processing"}
REQUIRED_DOMAIN_KEYWORDS = {"nlp", "information retrieval", "rag", "ranking", "embeddings", "search"}
MIN_YEARS_FOR_EXTERNAL_VALIDATION = 5

# Red Flag Logic
MAX_ALLOWED_RED_FLAGS = 2 
RED_FLAG_PENALTY = 0.5 

# Production vs Research Signals 
PRODUCTION_KEYWORDS = {"deployed", "shipped", "production", "scaled", "latency", "uptime", "cluster", "ci/cd", "end-to-end"}
RESEARCH_KEYWORDS = {"explored", "studied", "researched", "paper", "theoretical", "experimented"}

# Location & Logistics 
LOCATION_BONUSES = {
    "pune": 1.2, "noida": 1.2, "hyderabad": 1.1, "mumbai": 1.1, "delhi": 1.1, "india": 1.0
}
DEFAULT_LOCATION_MULTIPLIER = 0.5 
IDEAL_TOTAL_EXP = (6, 8)
IDEAL_ML_EXP = (4, 5)
EXP_SWEET_SPOT_BONUS = 1.1

# Behavioral Multiplier Logic
SIGNAL_MODIFIERS = {
    "open_to_work_bonus": 0.15,
    "inactive_penalty": -0.30,
    "low_response_penalty": -0.20,
    "high_response_bonus": 0.10,
    "high_demand_bonus": 0.10,
    "high_completion_bonus": 0.10,
    "verified_bonus": 0.05,
    "github_active_bonus": 0.05,
    "fast_notice_bonus": 0.10,
    "long_notice_penalty": -0.15,
}

# File Paths 
CANDIDATES_FILE = "data/candidates.jsonl" 
EMBEDDINGS_PATH = "artifacts/embeddings.npy"
FAISS_INDEX_PATH = "artifacts/faiss.index"
JD_EMBEDDING_PATH = "artifacts/jd_embedding.npy"