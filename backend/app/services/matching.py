def score_match(resume_skills: list[str], required: list[str], preferred: list[str], certificates: list[str] | None = None) -> dict:
    resume_set = {skill.lower() for skill in resume_skills}
    required_set = {skill.lower() for skill in required}
    preferred_set = {skill.lower() for skill in preferred}
    required_score = ratio_score(resume_set, required_set)
    preferred_score = ratio_score(resume_set, preferred_set)
    project_score = 82 if {"python", "java", "vue", "rag", "sql"} & resume_set else 62
    tool_score = 86 if {"docker", "git", "linux", "kubernetes"} & resume_set else 58
    scenario_score = 76
    cert_score = 88 if certificates else 55
    total = (
        required_score * 0.4
        + preferred_score * 0.15
        + project_score * 0.2
        + tool_score * 0.1
        + scenario_score * 0.1
        + cert_score * 0.05
    )
    missing = [skill for skill in required if skill.lower() not in resume_set]
    return {
        "total_score": round(total, 1),
        "required_skill_score": required_score,
        "preferred_skill_score": preferred_score,
        "project_score": project_score,
        "tool_score": tool_score,
        "scenario_score": scenario_score,
        "certificate_score": cert_score,
        "missing_skills": missing,
        "suggestions": [f"围绕 {skill} 做一个小任务，并在简历里写清楚你负责的部分、处理过程和结果" for skill in missing[:5]]
        or ["把最近做过的项目整理成一段经历：背景、你的工作、结果和复盘"],
    }


def ratio_score(candidate: set[str], target: set[str]) -> float:
    if not target:
        return 100
    return round(len(candidate & target) / len(target) * 100, 1)
