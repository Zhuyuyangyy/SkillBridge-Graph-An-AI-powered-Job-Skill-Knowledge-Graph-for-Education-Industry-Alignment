import random
import sys
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy import inspect, text

from app.db.database import Base, SessionLocal, engine
from app.models import (
    CandidateProfile,
    DataSource,
    EvolutionEvent,
    JobEntity,
    JobSkillRelation,
    MatchReport,
    ParsedJD,
    RawJD,
    Resume,
    ResumeSkill,
    ReviewTask,
    SkillEntity,
    TestCase,
    User,
)
from app.services.constants import JOB_NAMES, JOB_PROFILES, SCENARIOS, SKILLS
from app.services.emerging_jobs import build_emerging_candidate
from app.services.jd_parser import text_hash
from app.services.matching import score_match
from app.services.auth import hash_password

DOMAINS = ["人工智能", "数据技术", "软件研发", "物联网", "智能系统", "安全合规", "产业数字化"]


def reset_database() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def seed_database() -> None:
    Base.metadata.create_all(bind=engine)
    migrate_database()
    db = SessionLocal()
    try:
        if db.scalar(select(User).limit(1)):
            ensure_minimum_test_cases(db)
            db.commit()
            return
        seed_users(db)
        sources = seed_sources(db)
        skills = seed_skills(db)
        jobs = seed_jobs(db)
        seed_relations(db, jobs, skills)
        seed_raw_jds(db, sources)
        seed_parsed_jds(db)
        seed_evolution(db, jobs)
        resumes = seed_resumes(db)
        seed_reports(db, resumes, jobs)
        seed_review_tasks(db)
        seed_test_cases(db)
        db.commit()
    finally:
        db.close()


def seed_sources(db):
    sources = []
    names = ["招聘平台样本库", "企业官网岗位页", "校招数据集", "行业报告与白皮书", "历史 JD 归档"]
    for idx, name in enumerate(names):
        source = DataSource(
            source_name=name,
            data_type="岗位 JD",
            domain=DOMAINS[idx % len(DOMAINS)],
            uploaded_at=datetime.utcnow() - timedelta(days=idx * 3),
            data_count=120 - idx * 13,
            duplicate_rate=round(0.03 + idx * 0.018, 3),
            noise_rate=round(0.04 + idx * 0.015, 3),
            quality_score=round(92 - idx * 3.6, 1),
            status="processed" if idx != 3 else "processing",
        )
        db.add(source)
        sources.append(source)
    db.flush()
    return sources


def migrate_database() -> None:
    inspector = inspect(engine)
    if not inspector.has_table("candidate_profiles"):
        return
    columns = {column["name"] for column in inspector.get_columns("candidate_profiles")}
    with engine.begin() as connection:
        if "avatar_url" not in columns:
            connection.execute(text("ALTER TABLE candidate_profiles ADD COLUMN avatar_url TEXT DEFAULT ''"))


def seed_skills(db):
    skills = []
    for idx, name in enumerate(SKILLS):
        skill = SkillEntity(
            name=name,
            category=category_for_skill(name),
            description=f"{name} 是岗位能力图谱中的技能实体，用于刻画岗位要求、学习路径和人岗匹配分析。",
            evidence=f"seed: 由模拟 JD、行业岗位画像与项目案例共同抽取得到，样本批次 S{idx % 6 + 1}",
        )
        db.add(skill)
        skills.append(skill)
    db.flush()
    return skills


def seed_jobs(db):
    jobs = []
    for idx, name in enumerate(JOB_NAMES):
        profile = JOB_PROFILES.get(name, {})
        job = JobEntity(
            name=name,
            domain=profile.get("domain", DOMAINS[idx % len(DOMAINS)]),
            job_type=profile.get("job_type", "综合岗位"),
            level=profile.get("level", ["初级", "中级", "高级"][idx % 3]),
            description=profile.get("description", f"{name} 负责业务需求分析、方案设计、系统配置、效果评估和持续优化。"),
            is_emerging=profile.get("is_emerging", False),
            status="active",
            version=f"v1.{idx % 4}",
            evidence=f"seed: 来自招聘平台、企业官网、行业报告与技术社区的多源样本，岗位序号 J{idx + 1}",
        )
        db.add(job)
        jobs.append(job)
    db.flush()
    return jobs


def seed_relations(db, jobs, skills):
    for job_idx, job in enumerate(jobs):
        selected_names = infer_skill_names_for_job(job.name)
        selected = [skill for skill in skills if skill.name in selected_names]
        if len(selected) < 12:
            start = (job_idx * 7) % len(skills)
            fallback = skills[start:start + 12]
            if len(fallback) < 12:
                fallback += skills[: 12 - len(fallback)]
            for skill in fallback:
                if skill not in selected:
                    selected.append(skill)
                if len(selected) >= 12:
                    break
        for idx, skill in enumerate(selected[:12]):
            db.add(
                JobSkillRelation(
                    job_id=job.id,
                    skill_id=skill.id,
                    relation_type="requires" if idx < 7 else "prefers",
                    weight=round(1 - idx * 0.035, 2),
                    evidence=f"seed: {job.name} 的岗位画像和模拟 JD 中出现 {skill.name}",
                )
            )


def seed_raw_jds(db, sources):
    for idx in range(120):
        job = JOB_NAMES[idx % len(JOB_NAMES)]
        profile = JOB_PROFILES.get(job, {})
        skill_slice = infer_skill_names_for_job(job)[:8]
        content = (
            f"{job} 岗位说明：{profile.get('description', job + ' 负责数字化业务建设。')} "
            f"重点场景：{SCENARIOS[idx % len(SCENARIOS)]}。"
            f"技能要求：{', '.join(skill_slice)}。"
            "需要具备清晰的文档能力、跨团队沟通能力、结果复盘意识和证据可追溯意识。"
        )
        db.add(
            RawJD(
                source_id=sources[idx % len(sources)].id,
                title=job,
                content=content,
                text_hash=text_hash(content),
                is_duplicate=idx % 19 == 0,
                created_at=datetime.utcnow() - timedelta(days=idx),
            )
        )


def seed_parsed_jds(db):
    rows = db.scalars(select(RawJD).limit(30)).all()
    for row in rows:
        skill_slice = [skill for skill in SKILLS if skill in row.content][:8]
        db.add(
            ParsedJD(
                raw_jd_id=row.id,
                job_name=row.title,
                domain=infer_domain(row.title),
                level=JOB_PROFILES.get(row.title, {}).get("level", "中级"),
                responsibilities='["需求分析","方案设计","落地实施","效果评估","文档沉淀"]',
                required_skills=str(skill_slice[:5]),
                preferred_skills=str(skill_slice[5:]),
                tools=str([skill for skill in skill_slice if skill in ["Docker", "Kubernetes", "Git", "Linux", "ECharts", "Milvus"]]),
                certificates="[]",
                experience="3-5 年",
                scenarios=str([scene for scene in SCENARIOS if scene in row.content] or ["企业数字化应用"]),
                confidence=0.86,
                evidence=f"seed: 解析自 RawJD#{row.id}",
            )
        )


def seed_evolution(db, jobs):
    for idx, job in enumerate(jobs[:12]):
        db.add(
            EvolutionEvent(
                job_id=job.id,
                added_skills=str([SKILLS[(idx * 5 + 1) % len(SKILLS)], SKILLS[(idx * 5 + 2) % len(SKILLS)]]),
                removed_skills=str([SKILLS[(idx * 5 + 3) % len(SKILLS)]]),
                modified_skills=str([{"skill": SKILLS[(idx * 5 + 4) % len(SKILLS)], "change": "由了解调整为熟悉，并要求提供项目证据"}]),
                update_note=f"{job.name} 的岗位画像在最近样本中更强调业务场景、证据来源和可落地成果。",
                data_sources=str(["招聘平台样本库", "企业官网岗位页", "行业报告与白皮书"]),
                confidence=round(0.74 + idx * 0.015, 2),
                version_record=str([f"v1.{idx}", f"v1.{idx + 1}"]),
                evidence=f"seed: {job.name} 最近 30 天 JD 技能频次、职责描述和行业样本变化",
                created_at=datetime.utcnow() - timedelta(days=idx * 4),
            )
        )


def seed_users(db):
    accounts = [
        {
            "username": "hr_admin",
            "password": "Demo@123",
            "role": "hr",
            "display_name": "企业 HR 管理员",
            "email": "hr@example.com",
            "organization": "数融智联示例企业",
        },
        {
            "username": "student_demo",
            "password": "Demo@123",
            "role": "candidate",
            "display_name": "学生求职者",
            "email": "student@example.com",
            "organization": "示例大学",
        },
        {
            "username": "candidate_demo",
            "password": "Demo@123",
            "role": "candidate",
            "display_name": "社会求职者",
            "email": "candidate@example.com",
            "organization": "个人用户",
        },
    ]
    for account in accounts:
        user = User(
            username=account["username"],
            password_hash=hash_password(account["password"]),
            role=account["role"],
            display_name=account["display_name"],
            email=account["email"],
            organization=account["organization"],
            phone="13800000000",
        )
        db.add(user)
        db.flush()
        if user.role == "candidate":
            db.add(
                CandidateProfile(
                    user_id=user.id,
                    real_name=user.display_name,
                    education="本科",
                    major="计算机科学与技术",
                    school="示例大学",
                    target_role="大模型应用工程师",
                    city="杭州",
                    expected_salary="12k-18k",
                    skills='["Python","SQL","RAG","项目管理"]',
                    certificates='["软考中级"]',
                    projects='["企业知识库问答系统","岗位能力图谱分析平台"]',
                    internships='["数据平台实习"]',
                    awards='["大学生软件设计竞赛"]',
                    self_summary="具备项目实践、数据分析和 AI 应用基础，希望从事新一代信息技术相关岗位。",
                    completeness=92,
                )
            )
    db.flush()


def seed_resumes(db):
    resumes = []
    templates = [
        ("林一", "本科", "计算机科学与技术", "示例大学", ["Python", "RAG", "LangChain", "FastAPI", "Docker"], "大模型应用工程师"),
        ("周青", "硕士", "软件工程", "示例理工大学", ["Java", "Spring Boot", "MySQL", "Redis", "Kafka"], "Java 开发工程师"),
        ("陈安", "本科", "数据科学", "示例财经大学", ["SQL", "Pandas", "ECharts", "数据治理", "数据质量"], "数据分析师"),
        ("赵禾", "本科", "物联网工程", "示例工业大学", ["MQTT", "Linux", "边缘计算", "传感器数据处理", "Docker"], "物联网开发工程师"),
        ("许宁", "硕士", "人工智能", "示例科技大学", ["机器学习", "深度学习", "PyTorch", "模型部署", "NLP"], "机器学习工程师"),
    ]
    for idx, (name, education, major, school, skills, intention) in enumerate(templates):
        candidate_users = db.scalars(select(User).where(User.role == "candidate").order_by(User.id)).all()
        owner = candidate_users[idx % len(candidate_users)] if candidate_users else None
        resume = Resume(
            user_id=owner.id if owner else None,
            name=name,
            education=education,
            major=major,
            school=school,
            projects=f"{name} 参与岗位能力分析平台、知识库问答、数据可视化或业务流程配置项目，能够说明项目目标、个人职责和量化结果。",
            internships="软件研发实习；数据平台实习" if idx % 2 == 0 else "算法工程实习；数字化项目助理",
            certificates="软考中级" if idx % 2 == 0 else "数据分析师证书",
            competitions="大学生软件设计竞赛",
            intention=intention,
            raw_text=f"姓名：{name}\n{education} {major} {school}\n熟悉 {'、'.join(skills)}，参与项目实践并能输出复盘报告。",
        )
        db.add(resume)
        db.flush()
        for skill in skills:
            db.add(ResumeSkill(resume_id=resume.id, skill_name=skill, level=random.choice(["基础", "中级", "高级"]), evidence="seed: 简历技能段落"))
        resumes.append(resume)
    return resumes


def seed_reports(db, resumes, jobs):
    for idx, resume in enumerate(resumes):
        job = jobs[idx % len(jobs)]
        relations = job.skill_relations
        required = [rel.skill.name for rel in relations if rel.relation_type == "requires"]
        preferred = [rel.skill.name for rel in relations if rel.relation_type == "prefers"]
        resume_skills = [skill.skill_name for skill in db.scalars(select(ResumeSkill).where(ResumeSkill.resume_id == resume.id)).all()]
        score = score_match(resume_skills, required, preferred, ["软考中级"])
        db.add(
            MatchReport(
                resume_id=resume.id,
                job_id=job.id,
                evidence=f"seed: Resume#{resume.id} 与 Job#{job.id} 的模拟匹配",
                total_score=score["total_score"],
                required_skill_score=score["required_skill_score"],
                preferred_skill_score=score["preferred_skill_score"],
                project_score=score["project_score"],
                tool_score=score["tool_score"],
                scenario_score=score["scenario_score"],
                certificate_score=score["certificate_score"],
                missing_skills=str(score["missing_skills"]),
                suggestions=str(score["suggestions"]),
            )
        )


def seed_review_tasks(db):
    candidates = [
        build_emerging_candidate("LLMOps 平台运营专员", ["LLMOps", "模型部署", "Prometheus", "数据资产运营"], "行业报告与白皮书", 0.76),
        build_emerging_candidate("AIGC 内容风控分析师", ["内容审核", "风险策略", "安全合规", "统计分析"], "招聘平台样本库", 0.84),
        build_emerging_candidate("AI 产品经理", ["产品设计", "需求分析", "RAG", "Prompt Engineering"], "企业官网岗位页", 0.82),
    ]
    for candidate in candidates:
        db.add(
            ReviewTask(
                task_type="新岗位",
                title=candidate["job_name"],
                description=candidate["definition"],
                confidence=candidate["emerging_index"],
                evidence=str(candidate["evidence"]),
                status="pending",
            )
        )
    for task_type, title in [("新技能", "数据资产运营"), ("删除技能", "过时脚本维护"), ("修改技能", "Prompt Engineering 熟练度调整")]:
        db.add(
            ReviewTask(
                task_type=task_type,
                title=title,
                description=f"{title} 需要人工确认后进入正式图谱。",
                confidence=0.68,
                evidence="seed: 低置信度规则触发",
                status="pending",
            )
        )


def seed_test_cases(db):
    ensure_minimum_test_cases(db)


def ensure_minimum_test_cases(db, target_count: int = 120):
    current = db.scalar(select(func.count(TestCase.id))) or 0
    if current >= target_count:
        return
    for idx in range(current, target_count):
        db.add(
            TestCase(
                case_type=["JD解析", "简历解析", "匹配分析"][idx % 3],
                name=f"测试用例-{idx + 1:02d}",
                expected="字段完整、证据可追溯、关键指标可复核",
                actual="需复核" if (idx + 1) % 17 == 0 else "通过",
                passed=(idx + 1) % 17 != 0,
            )
        )


def infer_skill_names_for_job(job_name: str) -> list[str]:
    mapping = {
        "大模型应用工程师": ["Python", "FastAPI", "RAG", "Prompt Engineering", "LangChain", "向量数据库", "Docker", "Linux", "Git", "OpenAPI", "LLMOps", "数据质量"],
        "AI 智能体开发工程师": ["Python", "LangChain", "RAG", "Prompt Engineering", "智能体编排", "工作流引擎", "OpenAPI", "权限管理", "Docker", "Linux", "安全合规", "数据质量"],
        "数据分析师": ["SQL", "Python", "Pandas", "统计分析", "BI 分析", "数据可视化", "ECharts", "用户画像", "A/B 测试", "数据质量", "需求分析", "业务流程建模"],
        "数据治理工程师": ["SQL", "Hive", "Spark", "数据治理", "数据血缘", "元数据管理", "数据质量", "数据仓库", "ETL", "安全合规", "项目管理", "业务流程建模"],
        "算法工程师": ["Python", "机器学习", "深度学习", "PyTorch", "TensorFlow", "特征工程", "模型评估", "NLP", "计算机视觉", "模型部署", "Docker", "Linux"],
        "Java 开发工程师": ["Java", "Spring Boot", "Spring Cloud", "MySQL", "Redis", "Kafka", "微服务", "RESTful API", "Docker", "Git", "Linux", "权限管理"],
        "前端开发工程师": ["Vue", "React", "TypeScript", "Element Plus", "ECharts", "AntV G6", "RESTful API", "Git", "权限管理", "数据可视化", "产品设计", "需求分析"],
        "物联网开发工程师": ["MQTT", "Linux", "嵌入式 Linux", "传感器数据处理", "物联网协议", "边缘计算", "Docker", "消息队列", "Python", "数据可视化", "项目管理", "安全合规"],
        "智能系统工程师": ["Python", "Linux", "Docker", "边缘计算", "模型部署", "RESTful API", "Prometheus", "Grafana", "物联网协议", "项目管理", "客户调研", "业务流程建模"],
        "机器学习工程师": ["Python", "机器学习", "Scikit-learn", "PyTorch", "模型评估", "模型部署", "Docker", "Linux", "特征工程", "NLP", "数据质量", "Git"],
        "AI 产品经理": ["产品设计", "需求分析", "RAG", "Prompt Engineering", "数据标注", "模型评估", "用户画像", "A/B 测试", "项目管理", "业务流程建模", "安全合规", "数据可视化"],
        "数据产品经理": ["SQL", "数据仓库", "元数据管理", "数据质量", "BI 分析", "需求分析", "产品设计", "权限管理", "用户画像", "数据资产运营", "项目管理", "业务流程建模"],
        "网络安全分析师": ["Linux", "安全合规", "权限管理", "日志分析", "风险策略", "Python", "SQL", "项目管理", "数据可视化", "业务流程建模", "内容审核", "Git"],
        "数字化解决方案顾问": ["需求分析", "客户调研", "项目管理", "业务流程建模", "数据治理", "知识图谱", "产品设计", "OpenAPI", "数据可视化", "安全合规", "智能制造", "BI 分析"],
        "数据资产运营专员": ["数据资产运营", "元数据管理", "数据质量", "BI 分析", "SQL", "需求分析", "项目管理", "权限管理", "数据可视化", "业务流程建模", "安全合规", "客户调研"],
        "AIGC 内容风控分析师": ["内容审核", "风险策略", "安全合规", "统计分析", "A/B 测试", "Prompt Engineering", "数据标注", "用户画像", "数据质量", "需求分析", "项目管理", "BI 分析"],
        "智能制造实施顾问": ["客户调研", "项目管理", "业务流程建模", "物联网协议", "MQTT", "数据可视化", "智能制造", "Linux", "SQL", "需求分析", "数据质量", "安全合规"],
        "低代码平台配置顾问": ["业务流程建模", "需求分析", "权限管理", "SQL", "产品设计", "RESTful API", "数据可视化", "项目管理", "客户调研", "数据质量", "安全合规", "Git"],
    }
    mapping.update(
        {
            "云计算架构师": ["云计算架构", "Kubernetes", "Docker", "Linux", "CI/CD", "Nginx", "Prometheus", "Grafana", "微服务", "云安全", "项目管理", "安全合规"],
            "DevOps 平台工程师": ["DevOps", "Git", "Docker", "Kubernetes", "Linux", "CI/CD", "Nginx", "Prometheus", "Grafana", "微服务", "日志分析", "项目管理"],
            "SRE 站点可靠性工程师": ["SRE", "Linux", "Kubernetes", "Prometheus", "Grafana", "Nginx", "日志分析", "微服务", "CI/CD", "Python", "安全合规", "项目管理"],
            "数据库管理员 DBA": ["数据库运维", "SQL", "MySQL", "Redis", "ClickHouse", "Hive", "Linux", "数据仓库", "ETL", "数据质量", "安全合规", "日志分析"],
            "网络工程师": ["网络协议", "Linux", "日志分析", "安全合规", "权限管理", "云安全", "项目管理", "客户调研", "Nginx", "Prometheus", "Grafana", "Git"],
            "云安全顾问": ["云安全", "安全合规", "权限管理", "日志分析", "Kubernetes", "Linux", "数据质量", "项目管理", "客户调研", "售前方案", "业务流程建模", "风险策略"],
            "渗透测试工程师": ["渗透测试", "漏洞扫描", "Linux", "网络协议", "Python", "日志分析", "安全合规", "权限管理", "RESTful API", "Git", "风险策略", "项目管理"],
            "测试开发工程师": ["测试自动化", "性能测试", "Python", "Java", "SQL", "RESTful API", "Docker", "Git", "CI/CD", "日志分析", "项目管理", "数据质量"],
            "数据仓库工程师": ["SQL", "Hive", "Spark", "Flink", "Kafka", "Airflow", "数据仓库", "ETL", "实时数仓", "湖仓一体", "元数据管理", "数据质量"],
            "BI 可视化分析师": ["SQL", "BI 分析", "统计分析", "数据可视化", "ECharts", "Tableau", "Power BI", "FineBI", "用户画像", "A/B 测试", "需求分析", "业务流程建模"],
            "IT 项目经理": ["项目管理", "需求分析", "业务流程建模", "客户调研", "安全合规", "售前方案", "产品设计", "数据可视化", "权限管理", "数据质量", "实施交付", "ITIL"],
            "ERP 实施顾问": ["ERP 实施", "业务流程建模", "需求分析", "SQL", "数据质量", "项目管理", "客户调研", "实施交付", "权限管理", "数据可视化", "售前方案", "安全合规"],
            "售前技术顾问": ["售前方案", "客户调研", "需求分析", "项目管理", "数据治理", "AI 应用", "云计算架构", "安全合规", "产品设计", "业务流程建模", "数据可视化", "OpenAPI"],
            "UI/UX 设计师": ["UI/UX 设计", "Figma", "产品设计", "需求分析", "用户画像", "数据可视化", "业务流程建模", "ECharts", "Vue", "TypeScript", "项目管理", "客户调研"],
            "数据标注项目经理": ["数据标注管理", "数据标注", "数据质量", "统计分析", "内容审核", "项目管理", "Prompt Engineering", "安全合规", "风险策略", "用户画像", "A/B 测试", "需求分析"],
            "技术支持工程师": ["Linux", "SQL", "RESTful API", "日志分析", "权限管理", "数据可视化", "客户调研", "项目管理", "Git", "Nginx", "安全合规", "业务流程建模"],
        }
    )
    return [skill for skill in mapping.get(job_name, SKILLS[:12]) if skill in SKILLS]


def infer_domain(job_name: str) -> str:
    return JOB_PROFILES.get(job_name, {}).get("domain", "新一代信息技术")


def category_for_skill(name: str) -> str:
    if name in ["Python", "Java", "Vue", "React", "FastAPI", "Flask", "Spring Boot", "Spring Cloud", "TypeScript"]:
        return "开发技术"
    if name in ["机器学习", "深度学习", "RAG", "Prompt Engineering", "LangChain", "知识图谱", "智能体编排", "LLMOps"]:
        return "人工智能"
    if name in ["数据治理", "数据血缘", "元数据管理", "数据质量", "Hadoop", "Spark", "Flink", "Hive", "数据资产运营"]:
        return "数据技术"
    if name in ["Docker", "Kubernetes", "Linux", "Git", "Nginx", "CI/CD", "Prometheus", "Grafana"]:
        return "工程工具"
    if name in ["需求分析", "产品设计", "业务流程建模", "项目管理", "客户调研"]:
        return "产品与交付"
    if name in ["内容审核", "风险策略", "安全合规", "权限管理"]:
        return "安全合规"
    return "通用能力"


if __name__ == "__main__":
    if "--reset" in sys.argv:
        reset_database()
    seed_database()
    total_jobs = SessionLocal().scalar(select(func.count(JobEntity.id)))
    print(f"Database ready. jobs={total_jobs}")
