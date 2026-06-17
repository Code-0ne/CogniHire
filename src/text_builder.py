from .config import PRODUCTION_KEYWORDS, RESEARCH_KEYWORDS

def  build_rich_txt(candidate):
    parts=[]
    summary = candidate.get("profile",{}).get("summary", "")
    if summary: parts.append(f"Summary: {summary}")

    hs = candidate.get("career_history", [])
    career_txt = [f"{j.get('title')} at {j.get('company')}: {j.get('description', '')}" for j in hs]
    if career_txt: parts.append("Experience: " + " | ".join(career_txt))

    skills = [s.get("name", "") for s in candidate.get("skills", [])]
    if skills: parts.append(f"Skills: {', '.join(skills)}")
    
    return " ".join(parts)

def scan_prod(text):
    return sum(1 for word in PRODUCTION_KEYWORDS if word in text.lower())

def scan_research(text):
    return sum(1 for word in RESEARCH_KEYWORDS if word in text.lower())