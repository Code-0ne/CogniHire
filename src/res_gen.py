def generate_reasoning(candidate, rank, final_score):
    if not candidate: return "Profile data missing."
    profile = candidate.get("profile", {})
    signals = candidate.get("redrob_signals", {})
    career = candidate.get("career_history", [])
    
    yoe = sum([j.get("duration_months", 0)/12 for j in career])
    top_title = career[0].get("title", "Engineer") if career else "Engineer"
    
    production_evidence = "relevant technical skills"
    for job in career:
        desc = job.get("description", "").lower()
        if any(word in desc for word in ["deployed", "shipped", "scaled", "production"]):
            production_evidence = f"production experience at {job.get('company', 'a product company')}"
            break

    reason = f"{top_title} with {yoe:.1f} years of experience. Strong match based on {production_evidence}. "
    
    nuances = []
    if signals.get("open_to_work_flag"): nuances.append("Actively open to work")
    if signals.get("notice_period_days", 30) < 30: nuances.append("fast notice period")
    
    location = profile.get("location", "").lower()
    if any(city in location for city in ["pune", "noida"]):
        nuances.append("ideal location match")
        
    if nuances: reason += f"Key signals: {', '.join(nuances)}."

    prefix = "Top-tier fit: " if rank <= 10 else "Strong match: " if rank <= 50 else "Relevant profile: "
    return f"{prefix}{reason}"
