"""图谱探索与能力演化模块。

该模块把 jobgraph 项目的「知识图谱探索」和「能力演化分析」能力融合进数融智联，
直接基于现有 SQLite 中的岗位、技能、岗位-技能关系和能力更新事件计算，
不依赖外部图数据库，作为一个自包含的可插拔模块提供以下接口：

- GET /api/graph/full        全图数据（含社区着色、中心度、节点大小）
- GET /api/graph/stats       图谱统计概览（节点/关系/社区/平均度/核心枢纽）
- GET /api/graph/communities 社区分布（按岗位领域聚类）
- GET /api/graph/path        两个岗位之间的技能迁移最短路径
- GET /api/graph/search      岗位/技能搜索
- GET /api/evolution/timeline 能力演化时间线（新增/删除/修改技能随时间变化）
- GET /api/evolution/hotspot  能力热点（上升/下降技能）
- GET /api/evolution/compare  领域能力对比
"""

import ast
from collections import defaultdict, deque

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import EvolutionEvent, JobEntity, JobSkillRelation, RawJD, SkillEntity

router = APIRouter(prefix="/api", tags=["graph-explore"])

# 社区配色，与前端主题（蓝/青/紫/绿/橙）保持一致
COMMUNITY_PALETTE = [
    "#2563eb",  # 蓝
    "#06b6d4",  # 青
    "#7c3aed",  # 紫
    "#18b981",  # 绿
    "#f59e0b",  # 橙
    "#ec4899",  # 粉
    "#0ea5e9",  # 天蓝
    "#14b8a6",  # 蓝绿
    "#f43f5e",  # 玫红
    "#8b5cf6",  # 紫罗兰
]


def _parse_list(value) -> list:
    """把种子数据里的字段解析成列表，兼容 "['a','b']"、含字典的列表以及 "a,b" 逗号串。"""
    if not value:
        return []
    if isinstance(value, list):
        return value
    text = str(value).strip()
    try:
        parsed = ast.literal_eval(text)
        return parsed if isinstance(parsed, list) else [parsed]
    except (SyntaxError, ValueError):
        return [item.strip() for item in text.strip("[]").split(",") if item.strip()]


def _skill_names(value) -> list[str]:
    """把技能列表统一成名称字符串，兼容 [{'skill': 'Redis', 'change': ...}] 这类结构。"""
    names = []
    for item in _parse_list(value):
        if isinstance(item, dict):
            name = item.get("skill") or item.get("name")
            if name:
                names.append(str(name))
        elif item:
            names.append(str(item))
    return names


def _build_graph(db: Session):
    """从数据库构建图结构，并计算社区、度数、中心度。返回一个上下文字典。"""
    jobs = db.scalars(select(JobEntity)).all()
    skills = db.scalars(select(SkillEntity)).all()
    relations = db.scalars(select(JobSkillRelation)).all()

    # 1) 社区 = 岗位领域(domain)。为每个领域分配稳定的索引与颜色。
    domains = sorted({(job.domain or "其他") for job in jobs})
    domain_index = {domain: idx for idx, domain in enumerate(domains)}

    skill_by_id = {skill.id: skill for skill in skills}
    job_by_id = {job.id: job for job in jobs}

    # 2) 技能归属社区：归到与它连接权重最大的岗位所属领域。
    skill_domain_weight: dict[int, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    degree: dict[str, int] = defaultdict(int)
    adjacency: dict[str, set] = defaultdict(set)
    edges = []

    for rel in relations:
        job = job_by_id.get(rel.job_id)
        skill = skill_by_id.get(rel.skill_id)
        if not job or not skill:
            continue
        job_node = f"job-{job.id}"
        skill_node = f"skill-{skill.id}"
        weight = float(rel.weight or 1)
        skill_domain_weight[skill.id][job.domain or "其他"] += weight
        degree[job_node] += 1
        degree[skill_node] += 1
        adjacency[job_node].add(skill_node)
        adjacency[skill_node].add(job_node)
        edges.append(
            {
                "source": job_node,
                "target": skill_node,
                "weight": round(weight, 2),
                "relation": rel.relation_type or "requires",
                "evidence": rel.evidence or "",
            }
        )

    skill_community: dict[int, int] = {}
    for skill in skills:
        weights = skill_domain_weight.get(skill.id)
        if weights:
            best_domain = max(weights.items(), key=lambda kv: kv[1])[0]
        else:
            best_domain = domains[0] if domains else "其他"
        skill_community[skill.id] = domain_index.get(best_domain, 0)

    max_degree = max(degree.values()) if degree else 1

    return {
        "jobs": jobs,
        "skills": skills,
        "edges": edges,
        "domains": domains,
        "domain_index": domain_index,
        "skill_community": skill_community,
        "degree": degree,
        "adjacency": adjacency,
        "max_degree": max_degree,
    }


def _job_node(job, ctx) -> dict:
    node_id = f"job-{job.id}"
    deg = ctx["degree"].get(node_id, 0)
    community = ctx["domain_index"].get(job.domain or "其他", 0)
    return {
        "id": node_id,
        "label": job.name,
        "type": "job",
        "community": community,
        "communityName": job.domain or "其他",
        "color": COMMUNITY_PALETTE[community % len(COMMUNITY_PALETTE)],
        "degree": deg,
        "centrality": round(deg / ctx["max_degree"], 2),
        "level": job.level,
        "isEmerging": bool(job.is_emerging),
        "size": round(26 + deg * 2.2, 1),
        "evidence": job.evidence or "",
    }


def _skill_node(skill, ctx) -> dict:
    node_id = f"skill-{skill.id}"
    deg = ctx["degree"].get(node_id, 0)
    community = ctx["skill_community"].get(skill.id, 0)
    return {
        "id": node_id,
        "label": skill.name,
        "type": "skill",
        "community": community,
        "communityName": ctx["domains"][community] if ctx["domains"] else "其他",
        "color": COMMUNITY_PALETTE[community % len(COMMUNITY_PALETTE)],
        "category": skill.category,
        "degree": deg,
        "centrality": round(deg / ctx["max_degree"], 2),
        "size": round(14 + deg * 1.8, 1),
        "evidence": skill.evidence or "",
    }


@router.get("/graph/full")
def graph_full(
    keyword: str = Query(default=""),
    community: int | None = Query(default=None),
    limit: int = Query(default=320, ge=20, le=1000),
    db: Session = Depends(get_db),
):
    ctx = _build_graph(db)
    nodes = [_job_node(job, ctx) for job in ctx["jobs"]]
    nodes += [_skill_node(skill, ctx) for skill in ctx["skills"]]

    kw = keyword.strip().lower()
    if kw:
        nodes = [n for n in nodes if kw in n["label"].lower()]
    if community is not None:
        nodes = [n for n in nodes if n["community"] == community]

    # 优先保留度数高的节点
    nodes.sort(key=lambda n: n["degree"], reverse=True)
    nodes = nodes[:limit]
    node_ids = {n["id"] for n in nodes}
    edges = [e for e in ctx["edges"] if e["source"] in node_ids and e["target"] in node_ids]

    return {
        "nodes": nodes,
        "edges": edges,
        "communities": _community_payload(ctx),
        "stats": _stats_payload(ctx),
    }


def _community_payload(ctx) -> list:
    job_count = defaultdict(int)
    skill_count = defaultdict(int)
    for job in ctx["jobs"]:
        job_count[ctx["domain_index"].get(job.domain or "其他", 0)] += 1
    for skill in ctx["skills"]:
        skill_count[ctx["skill_community"].get(skill.id, 0)] += 1
    result = []
    for domain, idx in sorted(ctx["domain_index"].items(), key=lambda kv: kv[1]):
        result.append(
            {
                "index": idx,
                "name": domain,
                "color": COMMUNITY_PALETTE[idx % len(COMMUNITY_PALETTE)],
                "jobCount": job_count.get(idx, 0),
                "skillCount": skill_count.get(idx, 0),
                "count": job_count.get(idx, 0) + skill_count.get(idx, 0),
            }
        )
    result.sort(key=lambda c: c["count"], reverse=True)
    return result


def _stats_payload(ctx) -> dict:
    node_count = len(ctx["jobs"]) + len(ctx["skills"])
    edge_count = len(ctx["edges"])
    top_hubs = sorted(
        (
            {
                "label": job.name,
                "type": "job",
                "degree": ctx["degree"].get(f"job-{job.id}", 0),
            }
            for job in ctx["jobs"]
        ),
        key=lambda h: h["degree"],
        reverse=True,
    )[:6]
    return {
        "nodeCount": node_count,
        "jobCount": len(ctx["jobs"]),
        "skillCount": len(ctx["skills"]),
        "edgeCount": edge_count,
        "communityCount": len(ctx["domains"]),
        "avgDegree": round(edge_count * 2 / node_count, 2) if node_count else 0,
        "topHubs": top_hubs,
    }


@router.get("/graph/stats")
def graph_stats(db: Session = Depends(get_db)):
    return _stats_payload(_build_graph(db))


@router.get("/graph/communities")
def graph_communities(db: Session = Depends(get_db)):
    return _community_payload(_build_graph(db))


@router.get("/graph/path")
def graph_path(
    from_job: int = Query(...),
    to_job: int = Query(...),
    db: Session = Depends(get_db),
):
    """在岗位-技能二部图上做 BFS，找出两个岗位之间的技能迁移路径。"""
    ctx = _build_graph(db)
    start = f"job-{from_job}"
    goal = f"job-{to_job}"
    adjacency = ctx["adjacency"]
    if start not in adjacency or goal not in adjacency:
        return {"found": False, "path": [], "shared": []}

    prev = {start: None}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        if current == goal:
            break
        for neighbor in adjacency[current]:
            if neighbor not in prev:
                prev[neighbor] = current
                queue.append(neighbor)

    if goal not in prev:
        return {"found": False, "path": [], "shared": []}

    chain = []
    cursor = goal
    while cursor is not None:
        chain.append(cursor)
        cursor = prev[cursor]
    chain.reverse()

    job_by_id = {f"job-{job.id}": job for job in ctx["jobs"]}
    skill_by_id = {f"skill-{skill.id}": skill for skill in ctx["skills"]}
    path = []
    for node_id in chain:
        if node_id in job_by_id:
            path.append({"id": node_id, "label": job_by_id[node_id].name, "type": "job"})
        elif node_id in skill_by_id:
            path.append({"id": node_id, "label": skill_by_id[node_id].name, "type": "skill"})

    # 两个岗位共享的技能（可直接迁移的能力）
    from_skills = adjacency.get(start, set())
    to_skills = adjacency.get(goal, set())
    shared = [
        skill_by_id[s].name
        for s in (from_skills & to_skills)
        if s in skill_by_id
    ]

    return {"found": True, "path": path, "shared": shared}


@router.get("/graph/search")
def graph_search(keyword: str = Query(default=""), db: Session = Depends(get_db)):
    ctx = _build_graph(db)
    kw = keyword.strip().lower()
    nodes = [_job_node(job, ctx) for job in ctx["jobs"]]
    nodes += [_skill_node(skill, ctx) for skill in ctx["skills"]]
    if kw:
        nodes = [n for n in nodes if kw in n["label"].lower()]
    nodes.sort(key=lambda n: n["degree"], reverse=True)
    return nodes[:30]


# ---------------------------------------------------------------------------
# 能力演化分析
# ---------------------------------------------------------------------------


@router.get("/evolution/timeline")
def evolution_timeline(db: Session = Depends(get_db)):
    """按时间聚合能力更新事件，展示新增/删除/修改技能的数量变化。"""
    events = db.scalars(select(EvolutionEvent).order_by(EvolutionEvent.created_at)).all()
    buckets: dict[str, dict] = {}
    detail = []
    for event in events:
        date_key = event.created_at.strftime("%Y-%m") if event.created_at else "未知"
        bucket = buckets.setdefault(date_key, {"date": date_key, "added": 0, "removed": 0, "modified": 0, "events": 0})
        added = _skill_names(event.added_skills)
        removed = _skill_names(event.removed_skills)
        modified = [
            {"name": item.get("skill") or item.get("name") or "", "change": item.get("change", "")}
            if isinstance(item, dict)
            else {"name": str(item), "change": ""}
            for item in _parse_list(event.modified_skills)
        ]
        bucket["added"] += len(added)
        bucket["removed"] += len(removed)
        bucket["modified"] += len(modified)
        bucket["events"] += 1
        job = db.scalar(select(JobEntity).where(JobEntity.id == event.job_id))
        versions = _skill_names(event.version_record)
        detail.append(
            {
                "jobId": event.job_id,
                "jobName": job.name if job else f"岗位#{event.job_id}",
                "date": date_key,
                "added": added,
                "removed": removed,
                "modified": modified,
                "note": event.update_note or "",
                "confidence": round(float(event.confidence or 0), 2),
                "version": versions[-1] if versions else "",
            }
        )
    timeline = sorted(buckets.values(), key=lambda b: b["date"])
    return {"timeline": timeline, "events": detail, "total": len(events)}


@router.get("/evolution/hotspot")
def evolution_hotspot(db: Session = Depends(get_db)):
    """能力热点：结合岗位需求量与演化事件中的新增/删除频次，给出上升与下降技能。"""
    relations = db.scalars(select(JobSkillRelation)).all()
    skills = {skill.id: skill for skill in db.scalars(select(SkillEntity)).all()}
    events = db.scalars(select(EvolutionEvent)).all()

    demand = defaultdict(int)
    weight_sum = defaultdict(float)
    for rel in relations:
        demand[rel.skill_id] += 1
        weight_sum[rel.skill_id] += float(rel.weight or 1)

    added_count = defaultdict(int)
    removed_count = defaultdict(int)
    for event in events:
        for name in _skill_names(event.added_skills):
            added_count[name] += 1
        for name in _skill_names(event.removed_skills):
            removed_count[name] += 1

    rising = []
    for skill_id, count in demand.items():
        skill = skills.get(skill_id)
        if not skill:
            continue
        growth = added_count.get(skill.name, 0)
        heat = round(count * 0.6 + weight_sum[skill_id] * 0.2 + growth * 3, 2)
        rising.append(
            {
                "name": skill.name,
                "category": skill.category,
                "demand": count,
                "growth": growth,
                "heat": heat,
            }
        )
    rising.sort(key=lambda s: s["heat"], reverse=True)

    declining = [
        {"name": name, "removed": count}
        for name, count in sorted(removed_count.items(), key=lambda kv: kv[1], reverse=True)
    ]

    emerging = [
        {"name": name, "growth": count}
        for name, count in sorted(added_count.items(), key=lambda kv: kv[1], reverse=True)
        if name not in {skills[s].name for s in demand}
    ][:8]

    return {"rising": rising[:12], "declining": declining[:8], "emerging": emerging}


@router.get("/evolution/compare")
def evolution_compare(db: Session = Depends(get_db)):
    """按岗位领域对比能力结构：每个领域的技能类别分布与热门技能。"""
    jobs = {job.id: job for job in db.scalars(select(JobEntity)).all()}
    skills = {skill.id: skill for skill in db.scalars(select(SkillEntity)).all()}
    relations = db.scalars(select(JobSkillRelation)).all()

    domain_category = defaultdict(lambda: defaultdict(int))
    domain_skill = defaultdict(lambda: defaultdict(float))
    for rel in relations:
        job = jobs.get(rel.job_id)
        skill = skills.get(rel.skill_id)
        if not job or not skill:
            continue
        domain = job.domain or "其他"
        domain_category[domain][skill.category or "其他"] += 1
        domain_skill[domain][skill.name] += float(rel.weight or 1)

    categories = sorted({skill.category or "其他" for skill in skills.values()})
    domains = sorted(domain_category.keys())
    matrix = []
    for domain in domains:
        row = {"domain": domain, "categories": {cat: domain_category[domain].get(cat, 0) for cat in categories}}
        top = sorted(domain_skill[domain].items(), key=lambda kv: kv[1], reverse=True)[:6]
        row["topSkills"] = [{"name": name, "weight": round(w, 2)} for name, w in top]
        matrix.append(row)

    return {"categories": categories, "domains": domains, "matrix": matrix}


# ---------------------------------------------------------------------------
# 证据链（借鉴挑战杯国奖项目的「可解释、可追溯」表达）
# ---------------------------------------------------------------------------


def _jd_snippets(db: Session, term: str, limit: int = 5) -> list[dict]:
    """在真实 JD 正文中检索包含该词的片段，作为证据来源（不编造）。"""
    term = (term or "").strip()
    if not term:
        return []
    rows = db.scalars(select(RawJD).where(RawJD.content.like(f"%{term}%")).limit(limit)).all()
    snippets = []
    for jd in rows:
        content = jd.content or ""
        idx = content.find(term)
        start = max(0, idx - 34)
        end = min(len(content), idx + len(term) + 46)
        snippet = content[start:end].replace("\n", " ").strip()
        if start > 0:
            snippet = "…" + snippet
        if end < len(content):
            snippet = snippet + "…"
        snippets.append(
            {
                "sourceType": "jd",
                "sourceId": f"jd_{jd.id}",
                "title": jd.title,
                "snippet": snippet,
            }
        )
    return snippets


@router.get("/graph/evidence")
def graph_evidence(
    node_type: str = Query(..., pattern="^(job|skill)$"),
    node_id: int = Query(...),
    db: Session = Depends(get_db),
):
    """节点证据链：证据说明 + 真实 JD 来源片段 + 来源数量 + 置信度 + 审核状态。"""
    if node_type == "job":
        job = db.scalar(select(JobEntity).where(JobEntity.id == node_id))
        if not job:
            raise HTTPException(status_code=404, detail="岗位不存在")
        rel_count = db.scalar(select(func.count(JobSkillRelation.id)).where(JobSkillRelation.job_id == node_id)) or 0
        sources = _jd_snippets(db, job.name)
        jd_hits = db.scalar(select(func.count(RawJD.id)).where(RawJD.content.like(f"%{job.name}%"))) or 0
        return {
            "name": job.name,
            "type": "job",
            "category": job.domain,
            "evidence": job.evidence or "",
            "confidence": 0.9 if not job.is_emerging else 0.72,
            "relationCount": rel_count,
            "sourceCount": jd_hits,
            "reviewStatus": "watching" if job.is_emerging else "approved",
            "sources": sources,
        }
    skill = db.scalar(select(SkillEntity).where(SkillEntity.id == node_id))
    if not skill:
        raise HTTPException(status_code=404, detail="技能不存在")
    rels = db.scalars(select(JobSkillRelation).where(JobSkillRelation.skill_id == node_id)).all()
    demand = len(rels)
    avg_weight = round(sum(float(r.weight or 1) for r in rels) / demand, 2) if demand else 0.0
    sources = _jd_snippets(db, skill.name)
    jd_hits = db.scalar(select(func.count(RawJD.id)).where(RawJD.content.like(f"%{skill.name}%"))) or 0
    return {
        "name": skill.name,
        "type": "skill",
        "category": skill.category,
        "evidence": skill.evidence or "",
        "confidence": avg_weight,
        "demand": demand,
        "sourceCount": jd_hits,
        "reviewStatus": "approved" if avg_weight >= 0.6 else "needs_review",
        "sources": sources,
    }


@router.get("/evolution/version-compare")
def evolution_version_compare(db: Session = Depends(get_db)):
    """岗位能力版本对比卡：由能力更新事件重建「上一版 vs 当前版」的能力差异。"""
    events = db.scalars(select(EvolutionEvent).order_by(EvolutionEvent.created_at.desc())).all()
    jobs = {job.id: job for job in db.scalars(select(JobEntity)).all()}
    skills_by_id = {skill.id: skill for skill in db.scalars(select(SkillEntity)).all()}
    cards = []
    for event in events:
        job = jobs.get(event.job_id)
        if not job:
            continue
        rel_skill_ids = [
            r.skill_id for r in db.scalars(select(JobSkillRelation).where(JobSkillRelation.job_id == event.job_id)).all()
        ]
        current = [skills_by_id[sid].name for sid in rel_skill_ids if sid in skills_by_id]
        added = _skill_names(event.added_skills)
        removed = _skill_names(event.removed_skills)
        modified = [
            {"name": item.get("skill") or item.get("name") or "", "change": item.get("change", "")}
            if isinstance(item, dict)
            else {"name": str(item), "change": ""}
            for item in _parse_list(event.modified_skills)
        ]
        added_set = set(added)
        # 重建上一版能力集合：当前 - 本次新增 + 本次删除
        previous = [s for s in current if s not in added_set] + [s for s in removed if s not in current]
        versions = _skill_names(event.version_record)
        cards.append(
            {
                "jobId": event.job_id,
                "jobName": job.name,
                "domain": job.domain,
                "fromVersion": versions[0] if versions else "v1.0",
                "toVersion": versions[-1] if len(versions) > 1 else "v1.1",
                "added": added,
                "removed": removed,
                "modified": modified,
                "currentSkills": current[:16],
                "previousSkills": previous[:16],
                "note": event.update_note or "",
                "confidence": round(float(event.confidence or 0), 2),
                "evidence": event.evidence or "",
            }
        )
    return {"cards": cards, "total": len(cards)}
