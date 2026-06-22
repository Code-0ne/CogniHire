from src.ranker import main as run_pipeline

if __name__ == "__main__":
    print("🚀 Starting CogniHire Ranking Pipeline...")
    # This will execute the full pipeline: Sieve 1 -> Sieve 2 -> Cross-Encoder -> CSV Generation
    run_pipeline(output_file="team_PixelPioneers.csv")
    print("✅ Pipeline completed. Check team_PixelPioneers.csv for results.")
