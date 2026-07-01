# src/precompute.py
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import time
import multiprocessing
import numpy as np
import faiss
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

from .loader import load_candidates
from .text_builder import build_rich_txt
from .config import (
    EMBEDDING_MODEL, 
    EMBEDDINGS_PATH, 
    FAISS_INDEX_PATH, 
    JD_EMBEDDING_PATH,
    TARGET_JD
)

def setup_artifacts():
    if not os.path.exists("artifacts"):
        os.makedirs("artifacts")
        print("Created /artifacts directory.")

def generate_candidate_embeddings_parallel(model, candidates):

    print("Preparing rich text blocks...")
  
    text_blocks = [build_rich_txt(c) for c in tqdm(candidates, desc="Processing Profiles")]
    
    print(f"Encoding {len(text_blocks)} candidates using {EMBEDDING_MODEL}...")
    
    # Using standard encode instead of multi_process_pool to avoid potential deadlocks 
    # and "stuck" behavior during aggregation on some environments.
    embeddings = model.encode(
        text_blocks, 
        batch_size=128,
        show_progress_bar=True,
        convert_to_numpy=True
    )
    
    return np.array(embeddings).astype('float32')

def build_and_save_faiss_index(embeddings):
    print("🏗️  Indexing vectors with FAISS (Cosine Similarity)...")
    
    # L2 Normalize embeddings to use Inner Product as Cosine Similarity
    faiss.normalize_L2(embeddings)
    
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension) 
    index.add(embeddings)
    faiss.write_index(index, FAISS_INDEX_PATH)
    print(f"Index saved to {FAISS_INDEX_PATH}")

def main():
    start_time = time.time()
    
    target_jd = TARGET_JD

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
        jd_vec = model.encode([target_jd], convert_to_numpy=True).astype("float32")
        faiss.normalize_L2(jd_vec)
        
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
