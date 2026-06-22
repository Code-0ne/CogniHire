
import json
import pandas as pd
from tqdm import tqdm
from src.config import CANDIDATES_FILE


def load_candidates(input_file=None):
    candidates = []
    file_path = input_file if input_file else CANDIDATES_FILE
    print(f"🚀 Loading candidates from {file_path}...")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in tqdm(f, total=100000, desc="Reading JSONL"):
                if line.strip():
                    candidates.append(json.loads(line))
        print(f"Successfully loaded {len(candidates)} candidates.")
        return candidates
    except FileNotFoundError:
        print(f"Error: {CANDIDATES_FILE} not found.")
        return None


def validate_dataset(candidates):

    if not candidates:
        return False
    
    
    if len(candidates) != 100000:
        print(f"⚠️ Warning: Expected 100,000 candidates, found {len(candidates)}")
    
    
    required_keys = ["candidate_id", "profile", "career_history", "redrob_signals"]
    first_rec = candidates[0]
    missing = [key for key in required_keys if key not in first_rec]
    
    if missing:
        print(f"❌ Schema Error: Missing keys {missing} in candidate records.")
        return False
    
    print("✅ Dataset validation passed.")
    return True

if __name__ == "__main__":
    
    data = load_candidates()
    if data:
        validate_dataset(data)
