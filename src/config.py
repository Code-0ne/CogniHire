# --- Model Configurations ---
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# --- Sieve 1: Semantic Recall ---
TOP_K_RECALL = 3000  # Number of candidates to pull from FAISS

# --- Sieve 2: Trap & Quality Filters ---
# Honeypot Thresholds
MAX_SKILL_DURATION_MULTIPLIER = 4  # sum(skill_duration) > YOE * 48 months
MIN_EXPERIENCE_FOR_EXPERT = 12     # Months needed to be "Expert"

# Consulting Blacklist (The "Pure Consulting" Penalty)
CONSULTING_FIRMS = {
    "tcs", "tata consultancy services", "infosys", "wipro", 
    "accenture", "cognizant", "capgemini", "hcl", "tech mahindra"
}

# Production vs Research Signals
PRODUCTION_KEYWORDS = {"deployed", "shipped", "production", "scaled", "latency", "uptime", "cluster", "ci/cd"}
RESEARCH_KEYWORDS = {"explored", "studied", "researched", "paper", "theoretical", "experimented"}

# --- Behavioral Multiplier Weights ---
# Multiplier ranges from 0.6 to 1.25
WEIGHTS = {
    "last_active_recency": 0.15,      # More recent = better
    "open_to_work": 0.10,           # True = bonus
    "response_rate": 0.10,          # High rate = better
    "interview_completion": 0.10,   # High completion = better
    "notice_period_penalty": -0.15, # Higher notice = penalty
    "github_activity": 0.05         # Bonus for high activity
}

# --- Logistics ---
TARGET_LOCATIONS = {"bangalore", "hyderabad", "pune", "remote", "india"}
MAX_NOTICE_PERIOD = 30  # Days (Preferred)

# --- File Paths ---
CANDIDATES_FILE = "data/candidates.jsonl"
EMBEDDINGS_PATH = "artifacts/embeddings.npy"
FAISS_INDEX_PATH = "artifacts/faiss.index"
JD_EMBEDDING_PATH = "artifacts/jd_embedding.npy"
