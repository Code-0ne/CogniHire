import random

from src.trajectory_engine import calculate_trajectory_scores
from src.jd_parser import get_jd_cont

def generate_reasoning(candidate, rank, final_score, jd_text=None):
    if not candidate: return "Profile data missing."
    
    signals = candidate.get("redrob_signals", {})
    career = candidate.get("career_history", [])
    
    traj = calculate_trajectory_scores(candidate)

    # Parse uploaded JD (or fallback to default JD)
    jd = get_jd_cont(jd_text)
    
    total_months = sum([j.get("duration_months", 0) for j in career])
    yoe = round(total_months / 12, 1)
    top_title = career[0].get("title", "Engineer") if career else "Engineer"

    min_exp = jd.get("min_yoe")
    max_exp = jd.get("max_yoe")

    experience_summary = None
    experience_concern = None

    if min_exp is not None and yoe < min_exp:
        experience_concern = (
        f"slightly below preferred experience range ({yoe:.1f}y vs {min_exp}-{max_exp}y)"
    )
    elif max_exp is not None and yoe > max_exp:
        experience_summary = (
        f"above preferred experience range ({yoe:.1f}y); brings additional seniority"
    )
    else:
        experience_summary = "within target experience range"

    # 1. Core technical strengths (JD connection)
    strength_factors = []
    if traj["production_ml_years"] >= 3:
        strength_factors.append(
            f"{traj['production_ml_years']}y building production ML systems"
        )

    if traj["ranking_years"] > 0:
        strength_factors.append(
            f"{traj['ranking_years']}y developing ranking systems"
        )

    if traj["search_rec_years"] > 0:
        strength_factors.append(
            f"{traj['search_rec_years']}y in search and retrieval"
        )

    if traj["vector_db_deployments"] > 0:
        strength_factors.append(
            f"hands-on experience with {traj['vector_db_deployments']} vector database technologies"
        )
    
    # Mention specific top company if it's a product company
    if career:
        latest_company = career[0].get("company", "Unknown")
        # Use a simplified check for product-company status if available in trajectory
        if traj["product_company_years"] > 0:
            strength_factors.append(f"product experience at {latest_company}")

    core_strength = " | ".join(strength_factors) if strength_factors else "general AI engineering"
    required_hits = candidate.get("required_skill_hits", [])
    preferred_hits = candidate.get("preferred_skill_hits", [])
    system_hits = candidate.get("system_hits", [])

    match_summary = []

    if required_hits:
        match_summary.append(
            f"matched {len(required_hits)} required skills"
        )

    if preferred_hits:
        match_summary.append(
            f"matched {len(preferred_hits)} preferred skills"
        )

    if system_hits:
        match_summary.append(
            f"matched {len(system_hits)} system engineering requirements"
    )
        
    if experience_summary:
        match_summary.append(experience_summary)

    if match_summary:
        match_text = " | ".join(match_summary)
    else:
        match_text = "limited direct JD skill matches"

    # 2. Honest concerns & Gaps
    concerns = []
    
    resp_rate = signals.get("recruiter_response_rate", 0.0)
    notice = signals.get("notice_period_days", 30)

    if experience_concern:
        concerns.append(experience_concern)

    if notice >= 120:
        concerns.append(f"very long notice period ({notice}d) may delay hiring")
    elif notice > 60:
        concerns.append(f"extended notice period ({notice}d)")

    if resp_rate < 0.15:
        concerns.append("very limited recruiter engagement")
    elif resp_rate < 0.30:
        concerns.append("below-average recruiter engagement")

    if jd.get("production_required"):
        if traj["production_ml_years"] == 0: 
            concerns.append("limited evidence of production ML deployment")

    if jd.get("evaluation_frameworks"):
        if traj["eval_framework_score"] == 0: 
            concerns.append("no mention of eval metrics (NDCG/MAP)")
    
    concern_text = " | ".join(concerns) if concerns else "no critical gaps"

    # 3. Final Synthesis (Matching tone to rank)
    if rank <= 10:
        tone = "Excellent Match "
        connector = random.choice([
            " Highly aligned with the uploaded JD.",
            " Recommended for immediate recruiter review.",
            " Strong overall fit with minimal trade-offs.",
            " Excellent alignment across technical and production requirements."
        ])

    elif rank <= 30:
        tone = "Strong Match "
        connector = random.choice([
            " Strong overall fit with only minor trade-offs.",
            " Worth progressing to technical interviews.",
            " Strong technical fit with a few manageable gaps.",
            " Recommended for further evaluation."
        ])

    elif rank <= 60:
        tone = "Good Match "
        connector = random.choice([
            " Good alignment with the core requirements.",
            " Some gaps exist but the overall profile remains relevant.",
            " Suitable depending on team priorities.",
            " Reasonable fit for the target role."
        ])

    else:
        tone = "Potential Match "
        connector = random.choice([
            " Additional recruiter review is recommended.",
            " Would benefit from deeper technical evaluation.",
            " Several gaps should be validated during screening.",
            " May suit adjacent roles better."
        ])

    reasoning = (
        f"{tone}\n"
        f"Strengths: {core_strength}\n"
        f"Alignment: {match_text}\n"
        f"Considerations: {concern_text}\n"
        f"{connector}"
    ) 
    return reasoning
