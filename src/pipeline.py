import numpy as np
import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer, CrossEncoder
from src.sieve_engine import sieve_2
from src.ranker import rank_candidates
from src.res_gen import generate_reasoning
from src.config import *
from src.precompute import generate_candidate_embeddings_parallel, build_and_save_faiss_index, setup_artifacts

class CogniHireEngine:
    def __init__(self):
        self.embed_model = SentenceTransformer(EMBEDDING_MODEL, device="cpu")
        self.cross_model = CrossEncoder(CROSS_ENCODER_MODEL, device="cpu")
        self.index = None
        self.embeddings = None

    def load_artifacts(self, index_path=FAISS_INDEX_PATH, embeddings_path=EMBEDDINGS_PATH):
        print("📦 Loading precomputed artifacts...")
        self.index = faiss.read_index(index_path)
        self.embeddings = np.load(embeddings_path)

    def precompute_on_fly(self, candidates):
        """
        Runs the full precompute logic to generate physical artifacts on disk.
        Matches the workflow of precompute.py.
        """
        
        print("⚙️  Executing precompute.py workflow...")
        setup_artifacts()
        
        embeddings = generate_candidate_embeddings_parallel(self.embed_model, candidates)
        
        np.save(EMBEDDINGS_PATH, embeddings)
        print(f"✅ Embeddings saved to {EMBEDDINGS_PATH}")
        
        build_and_save_faiss_index(embeddings)
        
        print("Precomputing JD target vector...")
        jd_vec = self.embed_model.encode([TARGET_JD],convert_to_numpy=True).astype('float32')

        faiss.normalize_L2(jd_vec)

        np.save(JD_EMBEDDING_PATH, jd_vec)
        print(f"✅ JD embedding saved to {JD_EMBEDDING_PATH}")
        
        self.embeddings = embeddings
        dimension = embeddings.shape[1]
        faiss.normalize_L2(embeddings)
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings)
        
        print("✨ Precomputation workflow complete. Artifacts generated.")

    def run_pipeline(self, candidates, jd_text):
        # 1. Sieve 1: Semantic Recall (Using Dynamic/Precomputed Index)
        jd_vec = self.embed_model.encode([jd_text],convert_to_numpy=True).astype("float32")

        faiss.normalize_L2(jd_vec)
        
        D, I = self.index.search(jd_vec, TOP_K_RECALL)
        distances = D[0].tolist()
        top_indices = I[0].tolist()

        # 2. Sieve 2: Intelligence Filter
        scored_candidates = sieve_2(distances, top_indices, candidates,jd_text)

        # 3. Sieve 3: Precision Rerank (Using ranker.py logic)
        final_100 = rank_candidates(scored_candidates[:600], candidates, jd_text, self.cross_model)

        # 5. Reasoning Generation
        submission_data = []
        for rank, res in enumerate(final_100, 1):
             # Copy original candidate
            cand_obj = candidates[res["index"]].copy()

            # Preserve metadata generated during sieve/ranking
            cand_obj["required_skill_hits"] = res.get("required_skill_hits", [])
            cand_obj["preferred_skill_hits"] = res.get("preferred_skill_hits", [])
            cand_obj["system_hits"] = res.get("system_hits", [])
            reasoning = generate_reasoning(cand_obj,rank,res["score"],jd_text)

            submission_data.append({
                "candidate_id": res["candidate_id"],
                "rank": rank,
                "score": res["score"],
                "reasoning": reasoning
            })

        return pd.DataFrame(submission_data)
