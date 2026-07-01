from .config import PRODUCTION_KEYWORDS, RESEARCH_KEYWORDS, REQUIRED_DOMAIN_KEYWORDS
from src.trajectory_engine import calculate_trajectory_scores

def build_rich_txt(candidate):
    parts = []
    
    # 1. Summary with semantic marker
    summary = candidate.get("profile", {}).get("summary", "")
    if summary: 
        parts.append(f"[CANDIDATE SUMMARY]: {summary}")

    # 2. Career History with recency weighting and structural markers
    hs = candidate.get("career_history", [])
    if hs:
        exp_parts = []
        for i, j in enumerate(hs):
            role = j.get('title', 'Unknown Role')
            company = j.get('company', 'Unknown Company')
            desc = j.get('description', '')
            
            # Mark the most recent role for the model
            prefix = "[MOST RECENT ROLE]" if i == 0 else "[EXPERIENCE]"
            exp_parts.append(f"{prefix} Role: {role}, Company: {company}, Contribution: {desc}")
        
        parts.append(" [PROFESSIONAL HISTORY] " + " | ".join(exp_parts))

    # 3. Skills grouped and emphasized
    skills_list = candidate.get("skills", [])
    if skills_list:
        all_skills = [s.get("name", "") for s in skills_list]
        
        # Highlight skills that match our required domain keywords
        critical_skills = [s for s in all_skills if s.lower() in REQUIRED_DOMAIN_KEYWORDS]
        
        skills_txt = f"Skills: {', '.join(all_skills)}"
        if critical_skills:
            skills_txt = f"Critical Skills: {', '.join(critical_skills)} | All Skills: {', '.join(all_skills)}"
        
        parts.append(f"[SKILLS SET]: {skills_txt}")
    
    # 4. Derived Metrics (Experience Calculation)
    # Attempting to estimate total exp if dates are available, else marker
    try:
        # Simple proxy: if we have career history, we can at least note the count of roles
        role_count = len(hs)
        parts.append(f"[METRICS]: Total Roles Held: {role_count}")
    except Exception:
        pass

    # 5. Behavioral Signals (For CrossEncoder)
    sig = candidate.get("redrob_signals", {})
    if sig:
        sig_parts = [
            f"Open to Work: {'Yes' if sig.get('open_to_work_flag') else 'No'}",
            f"Notice: {sig.get('notice_period_days', 'N/A')} days",
            f"Recruiter Response: {sig.get('recruiter_response_rate', 'N/A')}",
            f"GitHub Score: {sig.get('github_activity_score', 'N/A')}",
            f"Saved by Recruiters: {sig.get('saved_by_recruiters_30d', 'N/A')}",
            f"Interview Rate: {sig.get('interview_completion_rate', 'N/A')}",
            f"Completeness: {sig.get('profile_completeness_score', 'N/A')}%"
        ]
        parts.append(f"[SIGNALS]: {' | '.join(sig_parts)}")

    # 6. Structured Trajectory Summary (For CrossEncoder Reasoning)
    
    traj = calculate_trajectory_scores(candidate)
    traj_summary = [
        f"Product Years: {traj['product_company_years']}",
        f"Ranking Years: {traj['ranking_years']}",
        f"Search Years: {traj['search_rec_years']}",
        f"Production ML: {traj['production_ml_years']}",
        f"Vector DBs: {traj['vector_db_deployments']}"
    ]
    parts.append(f"[TRAJECTORY SUMMARY]: {' | '.join(traj_summary)}")

    return " ".join(parts)

def scan_prod(text):
    return sum(1 for word in PRODUCTION_KEYWORDS if word in text.lower())

def scan_research(text):
    return sum(1 for word in RESEARCH_KEYWORDS if word in text.lower())