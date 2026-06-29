from src.config import REQUIRED_DOMAIN_KEYWORDS

def generate_reasoning(candidate, rank, final_score):
    if not candidate: return "Profile data missing."
    
    profile = candidate.get("profile", {})
    signals = candidate.get("redrob_signals", {})
    career = candidate.get("career_history", [])
    
    from src.trajectory_engine import calculate_trajectory_scores
    traj = calculate_trajectory_scores(candidate)
    
    total_months = sum([j.get("duration_months", 0) for j in career])
    yoe = round(total_months / 12, 1)
    top_title = career[0].get("title", "Engineer") if career else "Engineer"
    

    # Calculate a more discriminative "Technical Strength" score instead of raw AI skill count
    tech_score = (traj["production_ml_years"] * 2 + 
                  traj["ranking_years"] * 3 + 
                  traj["search_rec_years"] * 2 + 
                  traj["vector_db_deployments"] * 1)
    strength_label = f"Tech Score: {round(tech_score, 1)}"

    production_status = "no prod evidence"
    for job in career:
        desc = job.get("description", "").lower()
        if any(word in desc for word in ["deployed", "shipped", "scaled", "production"]):
            production_status = f"prod exp @ {job.get('company', 'ProductCo')}"
            break

    # 1. Core technical strengths (JD connection)
    strength_factors = []
    if traj["production_ml_years"] >= 3: strength_factors.append(f"strong prod ML background ({traj['production_ml_years']}y)")
    if traj["ranking_years"] > 0: strength_factors.append(f"specialized in ranking ({traj['ranking_years']}y)")
    if traj["search_rec_years"] > 0: strength_factors.append(f"search/retrieval expertise ({traj['search_rec_years']}y)")
    if traj["vector_db_deployments"] > 0: strength_factors.append(f"deployed {traj['vector_db_deployments']} vector DBs")
    
    # Mention specific top company if it's a product company
    if career:
        latest_company = career[0].get("company", "Unknown")
        # Use a simplified check for product-company status if available in trajectory
        if traj["product_company_years"] > 0:
            strength_factors.append(f"product experience at {latest_company}")

    core_strength = " | ".join(strength_factors) if strength_factors else "general AI engineering"

    # 2. Honest concerns & Gaps
    concerns = []
    
    resp_rate = signals.get("recruiter_response_rate", 0.0)
    notice = signals.get("notice_period_days", 30)

    if yoe < 5: concerns.append(f"short of 5y target ({yoe}y)")
    if yoe > 9: concerns.append(f"exceeds 9y preferred range ({yoe}y)")
    if notice > 60: concerns.append(f"high notice period ({notice}d)")
    if resp_rate < 0.3: concerns.append(f"low recruiter response ({resp_rate:.2f})")
    if traj["production_ml_years"] == 0: concerns.append("no verifiable prod deployment")
    if traj["eval_framework_score"] == 0: concerns.append("no mention of eval metrics (NDCG/MAP)")
    
    concern_text = " | ".join(concerns) if concerns else "no critical gaps"

    # 3. Final Synthesis (Matching tone to rank)
    if rank <= 10:
        tone = "Strong fit: "
        connector = " High alignment with JD."
    elif rank <= 30:
        tone = "Good fit: "
        connector = " Solid match with minor trade-offs."
    else:
        tone = "Marginal fit: "
        connector = " Lower alignment with core requirements."

    reasoning = f"{tone}{top_title} ({yoe}y). {core_strength}. Concerns: {concern_text}. {connector}"
    
    return reasoning
