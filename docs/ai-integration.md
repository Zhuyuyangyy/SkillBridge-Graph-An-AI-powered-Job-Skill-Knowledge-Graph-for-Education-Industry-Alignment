# AI 接入预留说明

当前系统默认使用 `AI_PROVIDER=mock`，所有智能分析由本地 `mock_llm.py`、规则服务和种子数据返回，不调用真实外部模型。

后续接入真实 AI 时，推荐使用兼容 Chat Completions 风格的服务，并通过环境变量配置：

```bash
AI_PROVIDER=openai_compatible
AI_API_BASE_URL=https://your-ai-host/v1
AI_API_KEY=your-api-key
AI_MODEL=your-model-name
```

## 统一 AI 接口

- `GET /api/ai/status`：查看当前 AI Provider、模型、配置状态和支持任务
- `POST /api/ai/analyze`：统一智能分析入口

请求示例：

```json
{
  "task_type": "jd_parse",
  "payload": {
    "text": "这里放 JD 文本"
  }
}
```

支持任务：

- `jd_parse`
- `resume_parse`
- `match_analysis`
- `learning_path`
- `emerging_job_analysis`
- `digital_interview`

## 已接入 AI 边界的功能

- JD 解析：`POST /api/jd/parse`
- 简历解析：`POST /api/resume/parse`
- 匹配分析建议：`POST /api/match-analysis`
- 学习路径说明：`GET /api/learning-path/{report_id}`
- 数字人面试官：`POST /api/digital-interviewer/interview`

这些接口目前仍返回 mock 结果，但业务调用链路已经经过 `ai_provider.py`。真实模型启用后，前端可以继续调用原接口。

## 数字人面试官预留

前端页面：`/digital-interviewer`

后端接口：

```json
POST /api/digital-interviewer/interview
{
  "job_name": "AI 产品经理",
  "resume_summary": "候选人简历摘要",
  "candidate_answer": "候选人回答",
  "stage": "opening"
}
```

当前接口返回：

- 下一题
- 面试官反馈
- 分数预览
- `video_stream` 占位字段
- `asr` 占位字段
- `tts` 占位字段
- `avatar_driver` 占位字段

后续接入数字人时，可以保持前端页面和业务接口不变，只替换真实数字人 SDK、ASR/TTS 服务和 `digital_interview` 的 AI 生成逻辑。

## 代码位置

- AI Provider 抽象：`backend/app/services/ai_provider.py`
- Mock 输出：`backend/app/services/mock_llm.py`
- API 路由：`backend/app/routers/api.py`
