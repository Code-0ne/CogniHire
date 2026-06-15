# test_day1.py
from src.loader import load_candidates, validate_dataset
from src.config import CANDIDATES_FILE
import os

def main():
    # 1. Check if data folder exists
    if not os.path.exists("data"):
        os.makedirs("data")
        print("Created data folder. Please place candidates.jsonl.gz inside it.")
        return

    # 2. Test Loader
    candidates = load_candidates()
    if candidates:
        # 3. Test Validation
        if validate_dataset(candidates):
            print("\n🎉 DAY 1 COMPLETE: System is ready for text building.")
        else:
            print("\n Validation failed.")
    else:
        print("\n❌ Loading failed.")

if __name__ == "__main__":
    main()
