"""统一 AI Provider 边界。

默认 AI_PROVIDER=mock 完全离线；配置 AI_PROVIDER=openai_compatible 加上
AI_API_BASE_URL / AI_API_KEY / AI_MODEL 后，JD 解析、简历解析、匹配建议、
学习路径与数字人面试官即走真实 Chat Completions 兼容接口。

面向答辩的三条可靠性设计（借鉴挑战杯改造方案的「异常回退」要求）：
1. 提示词内置字段级输出 schema，约束真实模型返回结构化 JSON；
2. 模型输出经 normalize_result 归一化——以本地 mock 结果为字段基线合并，
   保证下游路由需要的键（如 confidence / evidence）永远存在；
3. 真实接口任何一步失败（网络、鉴权、JSON 解析）自动回退 mock 并在响应中
   标注 fallback 与原因，演示现场不会因外部服务抖动而中断。
"""

import json
import os
import re
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
AI_TIMEOUT_SECONDS = float(os.getenv("AI_TIMEOUT_SECONDS", "45"))


class AIProviderError(RuntimeError):
    pass


def ai_status() -> dict:
    return {
        "provider": AI_PROVIDER,
        "model": AI_MODEL,
        "base_url_configured": bool(AI_API_BASE_URL),
        "api_key_configured": bool(AI_API_KEY),
        "enabled": AI_PROVIDER != "mock" and bool(AI_API_BASE_URL and AI_API_KEY),
        "fallback_to_mock": True,
        "timeout_seconds": AI_TIMEOUT_SECONDS,
        "supported_tasks": ["jd_parse", "resume_parse", "match_analysis", "learning_path", "emerging_job_analysis", "digital_interview"],
    }


def analyze_with_ai(task_type: str, payload: dict[str, Any]) -> dict:
    if AI_PROVIDER == "mock":
        return analyze_with_mock(task_type, payload)
    try:
        response = analyze_with_openai_compatible(task_type, payload)
        response["result"] = normalize_result(task_type, response["result"], payload)
        response["fallback"] = False
        return response
    except Exception as exc:  # noqa: BLE001 —— 真实接口任何异常都回退本地 mock，保证演示不中断
        fallback = analyze_with_mock(task_type, payload)
        fallback["fallback"] = True
        fallback["requested_provider"] = AI_PROVIDER
        fallback["requested_model"] = AI_MODEL
        fallback["fallback_reason"] = str(exc)[:300]
        return fallback


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
    messages = [
        {"role": "system", "content": "你是岗位能力图谱与人岗匹配分析助手。严格按照用户给出的 output_schema 返回 JSON 对象，不要输出 Markdown、注释或多余文字。"},
        {"role": "user", "content": prompt},
    ]
    try:
        # 优先请求 JSON 模式；部分兼容网关不支持 response_format，失败时降级重试一次
        data = _chat_completion(messages, response_format={"type": "json_object"})
    except AIProviderError as exc:
        if "response_format" in str(exc) or "400" in str(exc):
            data = _chat_completion(messages, response_format=None)
        else:
            raise

    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise AIProviderError(f"AI 接口返回结构异常：{str(data)[:200]}") from exc
    result = _extract_json(content)
    return {"provider": AI_PROVIDER, "model": AI_MODEL, "task_type": task_type, "result": result}


def _chat_completion(messages: list[dict], response_format: dict | None) -> dict:
    body: dict[str, Any] = {"model": AI_MODEL, "messages": messages, "temperature": 0.2}
    if response_format:
        body["response_format"] = response_format
    req = urllib.request.Request(
        f"{AI_API_BASE_URL}/chat/completions",
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {AI_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=AI_TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            detail = exc.read().decode("utf-8")[:200]
        except Exception:  # noqa: BLE001
            pass
        raise AIProviderError(f"AI 接口调用失败：HTTP {exc.code} {detail}") from exc
    except urllib.error.URLError as exc:
        raise AIProviderError(f"AI 接口调用失败：{exc}") from exc
    except json.JSONDecodeError as exc:
        raise AIProviderError("AI 接口返回了非 JSON 响应") from exc


def _extract_json(content: str) -> dict:
    """从模型输出中稳健提取 JSON 对象，兼容 ```json 代码块与前后缀噪声。"""
    text = (content or "").strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else {"raw_text": content}
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if 0 <= start < end:
            try:
                parsed = json.loads(text[start : end + 1])
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass
    return {"raw_text": content}


def normalize_result(task_type: str, result: Any, payload: dict[str, Any]) -> dict:
    """以本地 mock 输出为字段基线，把真实模型输出归一化成下游路由期望的结构。

    模型给出的非空同名字段覆盖基线；缺失/为空的字段保留基线默认值，
    保证 confidence、evidence 等关键键永远存在且类型正确。
    """
    if not isinstance(result, dict):
        result = {"raw_text": str(result)}
    baseline = analyze_with_mock(task_type, payload)["result"]
    merged = dict(baseline)
    for key, value in result.items():
        if value in (None, "", [], {}):
            continue
        if key in merged and isinstance(merged[key], list) and not isinstance(value, list):
            value = [value]
        merged[key] = value
    if "confidence" in merged:
        try:
            merged["confidence"] = round(max(0.0, min(1.0, float(merged["confidence"]))), 2)
        except (TypeError, ValueError):
            merged["confidence"] = baseline.get("confidence", 0.7)
    return merged


# 各任务的字段级输出 schema（值为类型/取值说明），用于约束真实模型的返回结构
OUTPUT_SCHEMAS: dict[str, dict] = {
    "jd_parse": {
        "job_name": "string，岗位名称",
        "domain": "string，所属领域",
        "level": "string，初级/中级/高级/专家",
        "responsibilities": ["string，岗位职责"],
        "required_skills": ["string，必备技能"],
        "preferred_skills": ["string，加分技能"],
        "tools": ["string，工具平台"],
        "certificates": ["string，证书"],
        "experience": "string，经验年限",
        "scenarios": ["string，行业场景"],
        "confidence": "number，0-1 置信度",
        "evidence": [{"source": "string，来源说明", "quote": "string，原文片段"}],
    },
    "resume_parse": {
        "name": "string，姓名",
        "education": "string，学历",
        "major": "string，专业",
        "school": "string，学校",
        "projects": ["string，项目经历"],
        "internships": ["string，实习经历"],
        "skills": [{"name": "string，技能名", "level": "string，基础/中级/高级"}],
        "certificates": ["string，证书"],
        "competitions": ["string，竞赛经历"],
        "intention": "string，岗位意向",
    },
    "match_analysis": {
        "summary": "string，匹配结论",
        "suggestions": ["string，改进建议"],
        "risk_points": ["string，风险提醒"],
    },
    "learning_path": {
        "stages": ["string，学习阶段名称"],
        "note": "string，路径生成说明",
    },
    "emerging_job_analysis": {
        "summary": "string，新岗位判断",
        "evidence_required": ["string，需要补充的证据来源"],
    },
    "digital_interview": {
        "interviewer_name": "string，面试官名称",
        "next_question": "string，下一道面试问题",
        "feedback": "string，对候选人回答的简短反馈",
        "score_preview": {"专业能力": "number 0-100", "项目表达": "number 0-100", "岗位匹配": "number 0-100", "逻辑沟通": "number 0-100"},
        "follow_up_tags": ["string，追问方向标签"],
    },
}


def build_prompt(task_type: str, payload: dict[str, Any]) -> str:
    task_prompts = {
        "jd_parse": "请解析岗位 JD 文本，抽取岗位名称、领域、等级、职责、必备/加分技能、工具、证书、经验、场景，给出 0-1 置信度，并为关键技能引用 JD 原文片段作为 evidence。",
        "resume_parse": "请解析简历文本，抽取姓名、学历、专业、学校、项目、实习、技能（含掌握程度）、证书、竞赛和岗位意向。",
        "match_analysis": "请根据简历信息和目标岗位要求做人岗匹配分析，给出匹配结论、逐条改进建议和风险提醒；建议要针对缺失技能，可执行、不空泛。",
        "learning_path": "请根据匹配报告和缺失技能生成阶段化学习路径，阶段由浅入深，并附一句路径生成说明。",
        "emerging_job_analysis": "请分析候选新岗位是否成立，给出判断摘要与仍需补充的证据来源清单。",
        "digital_interview": "请扮演数字人面试官：根据目标岗位、简历摘要和候选人本轮回答，生成下一道追问、简短反馈、四个维度的 0-100 评分和追问方向标签。",
    }
    return json.dumps(
        {
            "task": task_type,
            "instruction": task_prompts.get(task_type, "请完成结构化智能分析，并按 output_schema 返回 JSON。"),
            "output_schema": OUTPUT_SCHEMAS.get(task_type, {"summary": "string"}),
            "payload": payload,
        },
        ensure_ascii=False,
    )
