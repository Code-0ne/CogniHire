# src/precompute.py
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import time
import multiprocessing
import numpy as np
import faiss
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

from src.loader import load_candidates
from src.text_builder import build_rich_txt
from src.config import (
    EMBEDDING_MODEL, 
    EMBEDDINGS_PATH, 
    FAISS_INDEX_PATH, 
    JD_EMBEDDING_PATH
)

def setup_artifacts():
    if not os.path.exists("artifacts"):
        os.makedirs("artifacts")
        print("Created /artifacts directory.")

def generate_candidate_embeddings_parallel(model, candidates):

    print("Preparing rich text blocks...")
  
    text_blocks = [build_rich_txt(c) for c in tqdm(candidates, desc="Processing Profiles")]
    
    print(f"Encoding {len(text_blocks)} candidates in parallel using {EMBEDDING_MODEL}...")
    

    pool = model.start_multi_process_pool()
    
  
    embeddings = model.encode(
        text_blocks, 
        pool=pool, 
        batch_size=512,
        show_progress_bar=True
    )
    

    model.stop_multi_process_pool(pool)
    
    return np.array(embeddings).astype('float32')

def build_and_save_faiss_index(embeddings):
    print("🏗️  Indexing vectors with FAISS...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension) 
    index.add(embeddings)
    faiss.write_index(index, FAISS_INDEX_PATH)
    print(f"Index saved to {FAISS_INDEX_PATH}")

def main():
    start_time = time.time()
    

    target_jd = (
        "Senior AI Engineer. Expertise in embeddings, vector databases, and ranking systems. "
        "Must have shipped production-grade ML systems to real users. Strong Python skills. "
        "Focus on NDCG/MAP evaluation. Prefers Pune/Noida locations."
    )

    try:
        setup_artifacts()
        
        print(f"Initializing model: {EMBEDDING_MODEL}...")
        model = SentenceTransformer(EMBEDDING_MODEL, device="cpu")  
        
        candidates = load_candidates()
        if not candidates: return

    
        embeddings = generate_candidate_embeddings_parallel(model, candidates)
        np.save(EMBEDDINGS_PATH, embeddings)
        print(f"Embeddings saved to {EMBEDDINGS_PATH}")
        
        build_and_save_faiss_index(embeddings)
        
        print("Precomputing JD target vector...")
        jd_vec = model.encode([target_jd]).astype('float32')
        np.save(JD_EMBEDDING_PATH, jd_vec)
        
        end_time = time.time()
        print(f"\n✨ Pre-computation successful! Total time: {(end_time - start_time)/60:.2f} minutes.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    try:
        multiprocessing.set_start_method('spawn', force=True)
    except RuntimeError:
        pass
    main()
