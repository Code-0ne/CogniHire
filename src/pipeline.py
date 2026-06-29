# src/pipeline.py
import numpy as np
import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer, CrossEncoder
from src.text_builder import build_rich_txt
from src.sieve_engine import sieve_2
from src.ranker import rank_candidates
from src.res_gen import generate_reasoning
from src.config import *

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
        from src.precompute import generate_candidate_embeddings_parallel, build_and_save_faiss_index, setup_artifacts
        import numpy as np
        
        print("⚙️  Executing precompute.py workflow...")
        setup_artifacts()
        
        # 1. Generate Embeddings
        embeddings = generate_candidate_embeddings_parallel(self.embed_model, candidates)
        
        # 2. Save Embeddings to disk
        np.save(EMBEDDINGS_PATH, embeddings)
        print(f"✅ Embeddings saved to {EMBEDDINGS_PATH}")
        
        # 3. Build and Save FAISS Index to disk
        build_and_save_faiss_index(embeddings)
        
        # 4. Precompute and Save JD target vector (using the default TARGET_JD from config)
        from src.config import TARGET_JD, JD_EMBEDDING_PATH
        print("Precomputing JD target vector...")
        jd_vec = self.embed_model.encode([TARGET_JD]).astype('float32')
        np.save(JD_EMBEDDING_PATH, jd_vec)
        print(f"✅ JD embedding saved to {JD_EMBEDDING_PATH}")
        
        # 5. Update in-memory state for immediate use in run_pipeline
        self.embeddings = embeddings
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)
        
        print("✨ Precomputation workflow complete. Artifacts generated.")

    def run_pipeline(self, candidates, jd_text):
        # 1. Sieve 1: Semantic Recall (Using Dynamic/Precomputed Index)
        jd_vec = self.embed_model.encode([jd_text]).astype('float32')
        
        D, I = self.index.search(jd_vec, TOP_K_RECALL)
        distances = D[0].tolist()
        top_indices = I[0].tolist()

        # 2. Sieve 2: Intelligence Filter
        scored_candidates = sieve_2(distances, top_indices, candidates)

        # 3. Sieve 3: Precision Rerank (Using ranker.py logic)
        final_100 = rank_candidates(scored_candidates[:600], candidates, jd_text, self.cross_model)

        # 5. Reasoning Generation
        submission_data = []
        for rank, res in enumerate(final_100, 1):
            cand_obj = candidates[res["index"]]
            reasoning = generate_reasoning(cand_obj, rank, res["score"])
            submission_data.append({
                "candidate_id": res["candidate_id"],
                "rank": rank,
                "score": res["score"],
                "reasoning": reasoning
            })

        return pd.DataFrame(submission_data)
