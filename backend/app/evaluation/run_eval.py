"""一键评测复现脚本（借鉴挑战杯国奖项目「可复现、可量化、可展示错误案例」的评测表达）。

针对本系统三条核心能力做离线评测，产出统一的指标 summary 和错误案例，
可直接喂给前端「测试评估」页面，也可在答辩现场一条命令复现：

    cd backend
    python -m app.evaluation.run_eval

结果写入 backend/app/evaluation/reports/evaluation_summary.json。
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SAMPLES_DIR = BASE_DIR / "samples"
REPORTS_DIR = BASE_DIR / "reports"


@dataclass
class EvalResult:
    task: str
    task_label: str
    samples: int
    precision: float | None = None
    recall: float | None = None
    f1: float | None = None
    accuracy: float | None = None
    error_cases: list[dict] = field(default_factory=list)
    notes: str | None = None


def load_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def safe_div(num: float, den: float) -> float:
    return round(num / den, 4) if den else 0.0


def eval_skill_extraction(task: str, task_label: str, gold_path: Path, pred_path: Path) -> EvalResult:
    """集合级技能抽取评测：按 micro precision / recall / f1 计算，并记录错误案例。"""
    gold = {row["id"]: set(row.get("skills", [])) for row in load_jsonl(gold_path)}
    pred = {row["id"]: set(row.get("skills", [])) for row in load_jsonl(pred_path)}
    tp = fp = fn = 0
    error_cases: list[dict] = []
    for key, gold_skills in gold.items():
        pred_skills = pred.get(key, set())
        hit = gold_skills & pred_skills
        missed = gold_skills - pred_skills
        extra = pred_skills - gold_skills
        tp += len(hit)
        fp += len(extra)
        fn += len(missed)
        if missed or extra:
            error_cases.append(
                {
                    "id": key,
                    "missed": sorted(missed),
                    "extra": sorted(extra),
                }
            )
    precision = safe_div(tp, tp + fp)
    recall = safe_div(tp, tp + fn)
    f1 = safe_div(2 * precision * recall, precision + recall)
    return EvalResult(
        task=task,
        task_label=task_label,
        samples=len(gold),
        precision=precision,
        recall=recall,
        f1=f1,
        error_cases=error_cases[:10],
        notes="集合级技能抽取，micro 平均",
    )


def eval_match(gold_path: Path, pred_path: Path) -> EvalResult:
    """人岗匹配 Top-1 命中率评测，并记录错配案例。"""
    gold = {row["id"]: row.get("top1_job") for row in load_jsonl(gold_path)}
    pred = {row["id"]: row.get("top1_job") for row in load_jsonl(pred_path)}
    matched = 0
    error_cases: list[dict] = []
    for key, gold_job in gold.items():
        pred_job = pred.get(key)
        if gold_job == pred_job:
            matched += 1
        else:
            error_cases.append({"id": key, "gold": gold_job, "pred": pred_job})
    return EvalResult(
        task="job_match",
        task_label="人岗匹配 Top-1",
        samples=len(gold),
        accuracy=safe_div(matched, len(gold)),
        error_cases=error_cases[:10],
        notes="Top-1 岗位命中率",
    )


def run() -> list[EvalResult]:
    gold = SAMPLES_DIR / "gold"
    pred = SAMPLES_DIR / "pred"
    return [
        eval_skill_extraction("jd_extraction", "JD 技能抽取", gold / "jd_gold.jsonl", pred / "jd_pred.jsonl"),
        eval_skill_extraction("resume_extraction", "简历技能抽取", gold / "resume_gold.jsonl", pred / "resume_pred.jsonl"),
        eval_match(gold / "match_gold.jsonl", pred / "match_pred.jsonl"),
    ]


def main() -> None:
    results = run()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    summary = {
        "generated_by": "app.evaluation.run_eval",
        "task_count": len(results),
        "total_samples": sum(r.samples for r in results),
        "results": [asdict(r) for r in results],
    }
    out_path = REPORTS_DIR / "evaluation_summary.json"
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"\n评测结果已写入: {out_path}")


if __name__ == "__main__":
    main()
