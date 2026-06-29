# Model Configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"



TARGET_JD = """
Senior AI Engineer – Founding Team at Redrob AI.

Looking for engineers with 5–9 years of experience building production-grade
AI and Machine Learning systems deployed to real users.

Required Skills:
- Production experience with embeddings-based retrieval systems.
- Vector databases and hybrid search (FAISS, Pinecone, Qdrant, Milvus,
  Weaviate, OpenSearch, Elasticsearch).
- Strong Python engineering.
- Ranking systems, semantic search, recommendation systems,
  candidate matching and retrieval.
- Experience designing evaluation frameworks using
  NDCG, MAP, MRR, offline benchmarking and A/B testing.
- Experience deploying scalable production ML systems.

Preferred Skills:
- LoRA, QLoRA, PEFT.
- Learning-to-Rank.
- Distributed systems.
- Large-scale inference optimization.
- HRTech, recruiting or marketplace products.
- Open-source AI/ML contributions.

Preferred Candidate:
- Product-company experience.
- Recently written production code.
- Strong retrieval and ranking expertise.
- Active job seeker with good recruiter engagement.
- Short notice period.
- Located in or willing to relocate to Pune or Noida.

Avoid:
- Pure consulting backgrounds.
- Pure research without production deployments.
- Only recent LangChain/OpenAI demo projects.
- Engineers who haven't written production code recently.
- Computer Vision/Speech/Robotics specialists without NLP/IR.
- No external validation (GitHub, papers, talks) despite long experience.
"""

# Sieve 1 - Semantic Recall

TOP_K_RECALL = 3000
# Sieve 2 - Trap Detection & Quality Filters

MAX_AVG_TENURE_FOR_STABILITY = 1.8
MIN_YEARS_FOR_EXTERNAL_VALIDATION = 5

MAX_ALLOWED_RED_FLAGS = 2
RED_FLAG_PENALTY = 0.5

# Consulting Companies
 

CONSULTING_FIRMS = {
    "tcs",
    "tata consultancy services",
    "infosys",
    "wipro",
    "accenture",
    "cognizant",
    "capgemini",
    "hcl",
    "tech mahindra",
    "ibm",
    "deloitte",
    "ltimindtree",
}

# Domain Keywords
 

REQUIRED_DOMAIN_KEYWORDS = {
    "nlp",
    "information retrieval",
    "retrieval",
    "ranking",
    "semantic search",
    "dense retrieval",
    "hybrid retrieval",
    "vector search",
    "embeddings",
    "vector database",
    "hybrid search",
    "recommendation",
    "recommendation system",
    "candidate matching",
    "learning to rank",
    "faiss",
    "pinecone",
    "milvus",
    "qdrant",
    "weaviate",
    "opensearch",
    "elasticsearch",
    "sentence-transformers",
    "rag",
    "search",
}

WRONG_DOMAIN_KEYWORDS = {
    "computer vision",
    "opencv",
    "robotics",
    "speech",
    "audio",
    "signal processing",
    "medical imaging",
    "image classification",
    "autonomous driving",
}

FRAMEWORK_KEYWORDS = {
    "langchain",
    "llamaindex",
    "crewai",
    "autogen",
    "tutorial",
    "demo",
    "wrapper",
    "api-call",
}

SYSTEM_KEYWORDS = {
    "architecture",
    "distributed",
    "latency",
    "throughput",
    "optimization",
    "index",
    "indexing",
    "vector",
    "retrieval",
    "serving",
    "cache",
    "distributed inference",
    "faiss",
}

# Production vs Research Signals

PRODUCTION_KEYWORDS = {
    "production",
    "deployed",
    "deployment",
    "shipped",
    "scaled",
    "latency",
    "uptime",
    "cluster",
    "ci/cd",
    "end-to-end",
    "monitoring",
    "serving",
    "inference",
    "pipeline",
    "microservice",
    "docker",
    "kubernetes",
    "api",
    "index refresh",
    "retrieval",
    "recommendation",
    "airflow",
    "mlflow",
    "feature store",
    "redis",
    "kafka",
    "grpc",
}

RESEARCH_KEYWORDS = {
    "paper",
    "publication",
    "conference",
    "journal",
    "benchmark",
    "ablation",
    "experimented",
    "researched",
    "studied",
    "theoretical",
    "thesis",
    "phd",
}

# Experience Preferences

IDEAL_TOTAL_EXP = (6, 8)
IDEAL_ML_EXP = (4, 5)

EXP_SWEET_SPOT_BONUS = 1.10

EXP_SWEET_SPOT_BONUS = 1.10

# Location Preferences
 

LOCATION_BONUSES = {
    "pune": 1.20,
    "noida": 1.20,
    "hyderabad": 1.10,
    "mumbai": 1.10,
    "delhi": 1.10,
    "india": 1.00,
}

DEFAULT_LOCATION_MULTIPLIER = 0.50

# Behaviour Thresholds

FAST_NOTICE_DAYS = 30
LONG_NOTICE_DAYS = 60

HIGH_PROFILE_COMPLETENESS = 80
LOW_PROFILE_COMPLETENESS = 40

HIGH_RESPONSE_RATE = 0.80
LOW_RESPONSE_RATE = 0.20

# Behaviour Score Modifiers

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
    "production_exp_bonus": 0.20,
}

# Scoring Weights

SCORING_WEIGHTS = {
    "semantic": 0.50,
    "behavior": 0.20,
    "production": 0.15,
    "experience": 0.10,
    "location": 0.05,
}

# File Paths

CANDIDATES_FILE = "data/candidates.jsonl"

EMBEDDINGS_PATH = "artifacts/embeddings.npy"
FAISS_INDEX_PATH = "artifacts/faiss.index"
JD_EMBEDDING_PATH = "artifacts/jd_embedding.npy"