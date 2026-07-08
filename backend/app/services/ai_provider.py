import json
import os
import urllib.error
import urllib.request
from typing import Any

from app.services.mock_llm import mock_extract_jd, mock_resume_parse

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

AI_PROVIDER = os.getenv("AI_PROVIDER", "mock").lower()
AI_API_BASE_URL = os.getenv("AI_API_BASE_URL", "").rstrip("/")
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "mock-llm")


class AIProviderError(RuntimeError):
    pass


def ai_status() -> dict:
    return {
        "provider": AI_PROVIDER,
        "model": AI_MODEL,
        "base_url_configured": bool(AI_API_BASE_URL),
        "api_key_configured": bool(AI_API_KEY),
        "enabled": AI_PROVIDER != "mock" and bool(AI_API_BASE_URL and AI_API_KEY),
        "supported_tasks": ["jd_parse", "resume_parse", "match_analysis", "learning_path", "emerging_job_analysis", "digital_interview"],
    }


def analyze_with_ai(task_type: str, payload: dict[str, Any]) -> dict:
    if AI_PROVIDER == "mock":
        return analyze_with_mock(task_type, payload)
    return analyze_with_openai_compatible(task_type, payload)


def analyze_with_mock(task_type: str, payload: dict[str, Any]) -> dict:
    text = str(payload.get("text") or payload.get("jd_text") or payload.get("resume_text") or "")
    if task_type == "jd_parse":
        return {"provider": "mock", "task_type": task_type, "result": mock_extract_jd(text)}
    if task_type == "resume_parse":
        return {"provider": "mock", "task_type": task_type, "result": mock_resume_parse(text)}
    if task_type == "match_analysis":
        missing = payload.get("missing_skills") or ["RAG", "Docker", "项目证据"]
        return {
            "provider": "mock",
            "task_type": task_type,
            "result": {
                "summary": "这份简历和目标岗位有一定关联，但关键经历还不够集中。建议先把缺失技能对应的项目经历补起来，再调整简历里的表达顺序。",
                "suggestions": [f"为 {skill} 准备一段能讲清楚的经历：为什么做、你怎么做、最后有什么结果" for skill in missing[:5]],
                "risk_points": ["项目经历写得还不够具体", "行业场景经验需要再说明清楚"],
            },
        }
    if task_type == "learning_path":
        return {
            "provider": "mock",
            "task_type": task_type,
            "result": {
                "stages": ["基础补齐", "核心技能训练", "项目实践", "部署与复盘"],
                "note": "系统根据匹配报告、缺失技能和岗位能力要求生成个性化学习路径。",
            },
        }
    if task_type == "emerging_job_analysis":
        return {
            "provider": "mock",
            "task_type": task_type,
            "result": {
                "summary": "该岗位具备一定新兴趋势，需要结合多源样本和证据进一步确认。",
                "evidence_required": ["招聘平台 JD", "企业官网岗位页", "行业报告"],
            },
        }
    if task_type == "digital_interview":
        job_name = payload.get("job_name", "目标岗位")
        answer = payload.get("candidate_answer") or ""
        if answer:
            question = "请继续说一下这个项目最后怎么判断做得好不好？中间遇到过什么问题，你是怎么处理的？"
            feedback = "回答里已经有项目背景了，接下来可以把你的具体职责、关键取舍和最后结果讲得更清楚。"
        else:
            question = f"你好，我是本场数字人面试官。请先用 2 分钟介绍一下你与 {job_name} 最相关的一段项目经历。"
            feedback = "等待候选人回答。"
        return {
            "provider": "mock",
            "task_type": task_type,
            "result": {
                "interviewer_name": "数融面试官",
                "next_question": question,
                "feedback": feedback,
                "score_preview": {
                    "专业能力": 78,
                    "项目表达": 72,
                    "岗位匹配": 76,
                    "逻辑沟通": 80,
                },
                "follow_up_tags": ["项目经历", "岗位能力", "结果说明", "问题处理"],
                "sdk_placeholder": {
                    "video_stream": "interface-ready",
                    "tts": "interface-ready",
                    "asr": "interface-ready",
                    "avatar_driver": "interface-ready",
                },
            },
        }
    return {
        "provider": "mock",
        "task_type": task_type,
        "result": {"summary": "该任务已进入统一 AI Provider 调用链，可按业务场景扩展结构化输出。"},
    }


def analyze_with_openai_compatible(task_type: str, payload: dict[str, Any]) -> dict:
    if not AI_API_BASE_URL or not AI_API_KEY:
        raise AIProviderError("AI_PROVIDER 已切换为真实接口，但 AI_API_BASE_URL 或 AI_API_KEY 未配置")

    prompt = build_prompt(task_type, payload)
    body = {
        "model": AI_MODEL,
        "messages": [
            {"role": "system", "content": "你是岗位能力图谱与人岗匹配分析助手。请只返回 JSON，不要输出 Markdown。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }
    req = urllib.request.Request(
        f"{AI_API_BASE_URL}/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {AI_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise AIProviderError(f"AI 接口调用失败：{exc}") from exc

    content = data["choices"][0]["message"]["content"]
    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        result = {"raw_text": content}
    return {"provider": AI_PROVIDER, "model": AI_MODEL, "task_type": task_type, "result": result}


def build_prompt(task_type: str, payload: dict[str, Any]) -> str:
    task_prompts = {
        "jd_parse": "请解析岗位 JD，返回岗位名称、领域、等级、职责、必备技能、加分技能、工具、证书、经验、场景、置信度和 evidence。",
        "resume_parse": "请解析简历，返回姓名、学历、专业、学校、项目、实习、技能、证书、竞赛、岗位意向和技能等级。",
        "match_analysis": "请根据简历信息和目标岗位要求做人岗匹配分析，返回总分、维度得分、缺失技能、风险点和改进建议。",
        "learning_path": "请根据匹配报告和缺失技能生成阶段化学习路径，返回阶段、内容、项目、周期和前置技能。",
        "emerging_job_analysis": "请分析候选新岗位，返回新岗位指数依据、岗位定义、职责、技能、场景、风险和 evidence。",
        "digital_interview": "请扮演数字人面试官，根据目标岗位、简历摘要和候选人回答生成下一道面试问题、追问依据、简短反馈和维度评分。",
    }
    return json.dumps(
        {
            "task": task_type,
            "instruction": task_prompts.get(task_type, "请完成结构化智能分析，并返回 JSON。"),
            "payload": payload,
        },
        ensure_ascii=False,
    )
