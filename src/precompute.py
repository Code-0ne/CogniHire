
import os
import time
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
        print("Created /artifacts directory for model weights and indices.")

def generate_candidate_embeddings(model, candidates):

    print("Preparing rich text blocks for embedding...")

    text_blocks = [build_rich_txt(c) for c in tqdm(candidates, desc="Processing Profiles")]
    
    print(f"Encoding {len(text_blocks)} candidates using {EMBEDDING_MODEL}...")
    # convert_to_numpy=True is essential for FAISS compatibility
    embeddings = model.encode(
        text_blocks, 
        batch_size=512, 
        show_progress_bar=True, 
        convert_to_numpy=True
    )
    
    return embeddings.astype('float32')

def build_and_save_faiss_index(embeddings):

    print("Indexing vectors with FAISS...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension) 
    index.add(embeddings)
    
    faiss.write_index(index, FAISS_INDEX_PATH)
    print(f"Index successfully written to {FAISS_INDEX_PATH}")

def main():
    start_time = time.time()

    target_jd = (
        "Senior AI Engineer. Expertise in embeddings, vector databases, and ranking systems. "
        "Must have shipped production-grade ML systems to real users. Strong Python skills. "
        "Focus on NDCG/MAP evaluation. Prefers Pune/Noida locations."
    )

    try:
        setup_artifacts()
        
        # Initialize Model
        print(f"Initializing Sentence-Transformer: {EMBEDDING_MODEL}...")
        model = SentenceTransformer(EMBEDDING_MODEL)
        
        # Load Data
        candidates = load_candidates()
        if not candidates:
            print("No candidates loaded. Aborting pre-computation.")
            return

        # 1. Embeddings Generation
        embeddings = generate_candidate_embeddings(model, candidates)
        np.save(EMBEDDINGS_PATH, embeddings)
        print(f"Embeddings saved to {EMBEDDINGS_PATH}")
        
        # 2. Indexing
        build_and_save_faiss_index(embeddings)
        
        # 3. JD Vector
        print("Precomputing JD target vector...")
        jd_vec = model.encode([target_jd]).astype('float32')
        np.save(JD_EMBEDDING_PATH, jd_vec)
        print(f"JD Vector saved to {JD_EMBEDDING_PATH}")

        end_time = time.time()
        duration = (end_time - start_time) / 60
        print(f"\nPre-computation successful! Total time: {duration:.2f} minutes.")
        print("System is now ready for the Ranking Phase (Phase 2).")

    except Exception as e:
        print(f"A critical error occurred during pre-computation: {e}")
        # In a real repo, we'd use logging.exception(e) here

if __name__ == "__main__":
    main()
