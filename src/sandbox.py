import json
import numpy as np
import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer, CrossEncoder

from src.text_builder import build_rich_txt
from src.sieve_engine import sieve_2
from src.res_gen import generate_reasoning
from src.config import EMBEDDING_MODEL, CROSS_ENCODER_MODEL, TOP_K_RECALL

class CogniHireSandbox:
    def __init__(self):
        self.embed_model = SentenceTransformer(EMBEDDING_MODEL)
        self.cross_model = CrossEncoder(CROSS_ENCODER_MODEL)

    def process_pipeline(self, jsonl_content, jd_text):

        candidates = [json.loads(line) for line in jsonl_content.splitlines() if line.strip()]
        if not candidates:
            raise ValueError("The uploaded file contains no valid candidate data.")


        jd_vec = self.embed_model.encode([jd_text]).astype('float32')
        text_blocks = [build_rich_txt(c) for c in candidates]
        cand_embeddings = self.embed_model.encode(text_blocks).astype('float32')
        

        index = faiss.IndexFlatL2(cand_embeddings.shape[1])
        index.add(cand_embeddings)
        
  
        D, I = index.search(jd_vec, min(len(candidates), TOP_K_RECALL))
        top_indices = I[0].tolist()


        scored_candidates = sieve_2(top_indices, candidates)

        pairs = []
        candidate_ids = []
        indices = []
        for item in scored_candidates:
            pairs.append([jd_text, text_blocks[item["index"]]])
            candidate_ids.append(item["candidate_id"])
            indices.append(item["index"])

        cross_scores = self.cross_model.predict(pairs)

        results = []
        for i in range(len(cross_scores)):
            results.append({
                "candidate_id": candidate_ids[i], 
                "index": indices[i], 
                "score": float(cross_scores[i])
            })

        results.sort(key=lambda x: (-x["score"], x["candidate_id"]))
        final_100 = results[:100]

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
