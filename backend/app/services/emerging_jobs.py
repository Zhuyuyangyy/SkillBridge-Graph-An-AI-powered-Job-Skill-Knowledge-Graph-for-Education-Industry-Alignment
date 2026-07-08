def calculate_emerging_index(
    skill_growth_rate: float,
    multi_source_consistency: float,
    skill_combo_novelty: float,
    title_stability: float,
    scenario_diffusion: float,
) -> float:
    score = (
        skill_growth_rate * 0.3
        + multi_source_consistency * 0.25
        + skill_combo_novelty * 0.25
        + title_stability * 0.1
        + scenario_diffusion * 0.1
    )
    return round(score, 3)


def build_emerging_candidate(job_name: str, skills: list[str], source: str, index_seed: float) -> dict:
    score = calculate_emerging_index(index_seed, 0.82, 0.78, 0.74, 0.68)
    return {
        "job_name": job_name,
        "emerging_index": score,
        "related_skills": skills,
        "main_sources": [source, "招聘平台 JD", "行业报告", "技术社区文章"],
        "definition": f"{job_name} 是由新技术、新业务流程和新行业场景共同推动形成的岗位方向，强调业务理解、工具使用、数据证据和跨团队协作。",
        "responsibilities": ["识别业务场景和岗位边界", "设计可落地的流程和能力指标", "沉淀证据来源、评估指标和复盘报告"],
        "required_skills": skills[:5],
        "preferred_skills": skills[5:8],
        "scenarios": ["企业数字化应用", "智能制造", "智慧教育", "内容安全", "数据资产运营"],
        "review_status": "pending" if score < 0.78 else "approved",
        "evidence": [{"source": source, "quote": f"{job_name} 在多源样本中出现，并伴随 {skills[0]} 等能力要求增长"}],
    }
