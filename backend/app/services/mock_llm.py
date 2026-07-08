from app.services.constants import CERTIFICATES, JOB_NAMES, SCENARIOS, SKILLS, TOOLS


def mock_extract_jd(text: str) -> dict:
    normalized = text.lower()
    compact = normalized.replace(" ", "")
    job_name = next((name for name in JOB_NAMES if name.lower().replace(" ", "") in compact), "新一代信息技术岗位")
    found_skills = [skill for skill in SKILLS if skill.lower() in normalized or skill in text]
    if not found_skills:
        found_skills = ["Python", "SQL", "需求分析", "项目管理"]
    found_tools = [tool for tool in TOOLS if tool.lower() in normalized or tool in text]
    found_certs = [cert for cert in CERTIFICATES if cert in text]
    scenarios = [scene for scene in SCENARIOS if scene in text] or ["企业数字化应用"]
    confidence = min(0.96, 0.62 + len(found_skills) * 0.025)
    return {
        "job_name": job_name,
        "domain": infer_domain(job_name, found_skills),
        "level": infer_level(text),
        "responsibilities": [
            "分析业务场景并拆解岗位能力要求",
            "参与方案设计、系统落地、测试评估和持续优化",
            "沉淀可复用的流程文档、证据来源和评估指标",
        ],
        "required_skills": found_skills[:8],
        "preferred_skills": found_skills[8:14] or ["沟通协作", "工程化实践"],
        "tools": found_tools or ["Git", "Docker"],
        "certificates": found_certs,
        "experience": "1-3 年" if "初级" in text or "助理" in text else "3-5 年",
        "scenarios": scenarios,
        "confidence": round(confidence, 2),
        "evidence": [{"source": "JD 文本关键词", "quote": skill} for skill in found_skills[:5]],
    }


def infer_domain(job_name: str, skills: list[str]) -> str:
    if "数据" in job_name or {"Hive", "Spark", "Flink", "数据治理"} & set(skills):
        return "数据技术"
    if "AI" in job_name or "大模型" in job_name or {"RAG", "LangChain"} & set(skills):
        return "人工智能"
    if "安全" in job_name or {"安全合规", "风险策略", "内容审核"} & set(skills):
        return "安全合规"
    if "产品" in job_name or {"产品设计", "需求分析"} & set(skills):
        return "产品与策略"
    if "物联网" in job_name:
        return "物联网"
    return "新一代信息技术"


def infer_level(text: str) -> str:
    if "专家" in text or "架构" in text:
        return "专家"
    if "高级" in text or "5年" in text:
        return "高级"
    if "实习" in text or "初级" in text or "助理" in text:
        return "初级"
    return "中级"


def mock_resume_parse(text: str) -> dict:
    skills = [skill for skill in SKILLS if skill.lower() in text.lower() or skill in text]
    if not skills:
        skills = ["Python", "SQL", "需求分析"]
    name = "候选人"
    for marker in ["姓名：", "姓名:"]:
        if marker in text:
            name = text.split(marker, 1)[1].splitlines()[0].strip()[:20]
    return {
        "name": name,
        "education": "硕士" if "硕士" in text else "本科",
        "major": "计算机科学与技术" if "计算机" in text else "软件工程",
        "school": "示例大学",
        "projects": ["岗位能力图谱系统", "企业知识库问答系统"] if "RAG" in skills else ["数据分析平台"],
        "internships": ["软件研发实习", "数据平台实习"] if "实习" in text else [],
        "skills": [{"name": skill, "level": infer_skill_level(text, skill)} for skill in skills],
        "certificates": [cert for cert in CERTIFICATES if cert in text],
        "competitions": ["大学生软件设计竞赛"] if "竞赛" in text else [],
        "intention": next((name for name in JOB_NAMES if name in text), "新一代信息技术岗位"),
    }


def infer_skill_level(text: str, skill: str) -> str:
    idx = text.find(skill)
    window = text[max(0, idx - 20): idx + 40] if idx >= 0 else ""
    if any(word in window for word in ["精通", "主导", "深入"]):
        return "高级"
    if any(word in window for word in ["熟悉", "负责", "使用"]):
        return "中级"
    return "基础"
