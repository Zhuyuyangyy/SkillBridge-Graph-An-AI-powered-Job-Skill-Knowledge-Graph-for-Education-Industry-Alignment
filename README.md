# 数融智联岗位能力图谱构建与分析系统（融合 JobGraph 图谱能力）

面向新一代信息技术岗位的前后端分离项目。系统支持多源数据管理、JD 解析、新岗位发现、岗位能力更新、能力图谱展示、简历解析、人岗匹配分析、学习路径推荐、人工审核、测试评估、数字人面试官预留，以及求职者/学生与企业 HR 的分角色账号体系。

第一版默认使用本地规则、关键词匹配和 `mock_llm.py` 模拟模型输出，不调用真实外部大模型接口；后续可以通过统一 AI Provider 接口接入真实模型。

## 融合说明（JobGraph → 数融智联）

本仓库在数融智联 demo 的基础上，融合了 JobGraph 项目的两块特色能力，作为**自包含、可插拔的新增模块**接入，不改动数融智联原有页面与接口：

- **图谱探索（`/graph-explore`）**：在岗位-技能网络上做社区聚类着色、核心枢纽（中心度）识别、以及两个岗位之间的技能迁移最短路径分析；节点详情支持打开**证据链抽屉**，展示置信度、来源命中数、审核状态和真实 JD 语料来源片段（可解释、可追溯）。
- **能力演化（`/capability-evolution`）**：能力更新的时间线趋势、**岗位能力版本对比卡**（上一版 vs 当前版的新增/调整/淘汰能力）、能力热点（上升/新兴/淘汰技能）与领域能力结构对比。

此外，参考挑战杯国奖项目「可复现、可量化、可展示错误案例」的评测表达，新增一键评测复现脚本 `backend/app/evaluation/run_eval.py`：对 JD 技能抽取、简历技能抽取、人岗匹配三条能力产出统一的 precision/recall/f1、Top-1 准确率和错误案例，答辩时可一条命令复现。

两个模块**直接复用数融智联现有 SQLite 中的岗位、技能、岗位-技能关系和能力更新事件数据**，后端计算集中在 `backend/app/routers/graph_explore.py`，不依赖外部图数据库；前端为 `frontend/src/views/GraphExplore.vue` 与 `frontend/src/views/CapabilityEvolution.vue`，沿用原有 Element Plus 玻璃拟态主题，支持浅色/深色模式。

原始的三个项目压缩包（`jobgraph-server`、`jobgraph-web`、`shurong-zhilian`）作为归档保留在 `fightbei/` 目录下。

## 技术栈

- 前端：Vue 3、Vite、TypeScript、Pinia、Element Plus、ECharts、AntV G6
- 后端：Python、FastAPI、SQLAlchemy、SQLite
- 部署：Docker Compose、Windows 一键启动脚本

## 快速启动

### Windows 一键启动

在项目根目录双击 `start.bat`。

脚本会自动检查依赖、初始化 SQLite 数据库、启动后端和前端，并打开浏览器。数据库初始化不会重置已有账号和业务数据；只有手动执行 `python -m app.db.init_db --reset` 才会清空并重新生成种子数据。

停止服务时双击 `stop.bat`，会释放后端 `8000` 和前端 `5173` 端口。

### 后端

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m app.db.init_db
uvicorn app.main:app --reload --port 8000
```

接口文档：http://localhost:8000/docs

### 前端

```bash
cd frontend
npm install
npm run dev
```

前端地址：http://localhost:5173

### Docker Compose

```bash
docker compose up --build
```

前端：http://localhost:5173  
后端：http://localhost:8000

## 默认账号

初始化数据库后会生成以下演示账号：

| 角色 | 用户名 | 密码 | 说明 |
| --- | --- | --- | --- |
| 企业 HR | `hr_admin` | `Demo@123` | 可查看后台概览、数据源、JD、岗位、候选人、审核、评估和系统设置 |
| 求职者/学生 | `student_demo` | `Demo@123` | 可维护个人画像、解析简历、做匹配分析、查看学习路径和数字人面试 |
| 求职者/学生 | `candidate_demo` | `Demo@123` | 另一份候选人样例账号 |

登录页支持创建新账号。账号、密码哈希、角色、个人资料和候选人画像都保存在 SQLite 数据库中，复制整个项目文件夹时会一起带走。

新账号注册会校验用户名、真实姓名、邮箱、密码强度、确认密码和数学验证码。用户名需包含英文和数字；密码需包含数字，并在大写字母、小写字母、特殊符号中至少包含一种。

## 角色设计

系统把用户分成两类：

- 求职者/学生：关注个人画像、简历解析、人岗匹配、学习路径、能力图谱和数字人面试官。
- 企业 HR/管理者：关注数据源、岗位体系、新岗位发现、岗位能力更新、候选人管理、人工审核、测试评估和系统设置。

前端菜单和后端接口都做了角色校验。求职者不能访问 HR 候选人管理接口，HR 可以查看候选人提交的个人画像、简历数量、技能、证书、项目经历和最近简历。

详细设计见：[docs/account-roles.md](docs/account-roles.md)

## 核心页面

- `/login` 登录与创建账号
- `/personal-center` 求职者个人中心，维护个人画像
- `/hr-candidates` HR 候选人管理
- `/overview` 系统概览
- `/datasets` 数据源管理
- `/jd-parser` JD 解析
- `/jobs` 岗位管理
- `/emerging-jobs` 新岗位发现
- `/job-evolution` 岗位能力更新
- `/skill-graph` 能力图谱
- `/graph-explore` 图谱探索（社区聚类、核心枢纽、技能迁移路径 · 融合自 JobGraph）
- `/capability-evolution` 能力演化（时间线、能力热点、领域对比 · 融合自 JobGraph）
- `/resume-parser` 简历解析
- `/match-analysis` 匹配分析
- `/learning-path` 学习路径
- `/review-tasks` 人工审核
- `/evaluation` 测试评估
- `/digital-interviewer` 数字人面试官预留页面
- `/account-settings` 账号设置与密码修改

## 默认数据

初始化脚本会生成：

- 至少 120 条模拟岗位 JD
- 34 个岗位实体，覆盖研发、数据、云计算、安全、项目管理、实施、售前、设计、数据运营等方向
- 至少 110 个技能实体
- 178 项 IT 相关证书候选词典，个人中心支持分组搜索和自定义补充
- 5 份模拟简历，并绑定到候选人账号
- 能力图谱关系、岗位更新事件、人工审核任务、测试用例和匹配报告

所有岗位定义、技能关系和更新记录都带有 `evidence` 字段。低置信度内容进入人工审核模块，不直接写入正式图谱。

## AI 接入预留

当前默认：

```bash
AI_PROVIDER=mock
```

后续接入真实 AI 时，可配置：

```bash
AI_PROVIDER=openai_compatible
AI_API_BASE_URL=https://your-ai-host/v1
AI_API_KEY=your-api-key
AI_MODEL=your-model-name
```

已预留统一接口：

- `GET /api/ai/status`
- `POST /api/ai/analyze`
- `POST /api/digital-interviewer/interview`

JD 解析、简历解析、匹配建议、学习路径和数字人面试官都已经走统一 AI Provider 边界，后续替换模型服务时不需要大改前端。

更详细说明见：[docs/ai-integration.md](docs/ai-integration.md)

## 融合模块接口（图谱探索 / 能力演化）

以下接口由 `backend/app/routers/graph_explore.py` 提供，基于现有数据实时计算：

- `GET /api/graph/full`：全图数据（节点含社区、中心度、节点大小；附社区分布与统计）
- `GET /api/graph/stats`：图谱统计（节点/关系/社区数、平均度、核心枢纽）
- `GET /api/graph/communities`：社区分布（按岗位领域聚类）
- `GET /api/graph/path?from_job=&to_job=`：两个岗位间的技能迁移最短路径（BFS）
- `GET /api/graph/search?keyword=`：岗位/技能搜索
- `GET /api/graph/evidence?node_type=&node_id=`：节点证据链（置信度、来源命中、审核状态、真实 JD 来源片段）
- `GET /api/evolution/timeline`：能力变更时间线与事件明细
- `GET /api/evolution/version-compare`：岗位能力版本对比卡（上一版 vs 当前版）
- `GET /api/evolution/hotspot`：能力热点（上升/新兴/淘汰技能）
- `GET /api/evolution/compare`：领域能力结构对比

### 评测复现

```bash
cd backend
python -m app.evaluation.run_eval
# 结果写入 backend/app/evaluation/reports/evaluation_summary.json
```

## 测试

```bash
cd backend
pytest -q

cd ../frontend
npm run build
```

## 目录结构

```text
shurong-zhilian/
  backend/
    app/
      db/
      models/
      routers/
      schemas/
      seed/
      services/
      tests/
  frontend/
    src/
      api/
      components/
      layouts/
      router/
      stores/
      views/
  docs/
  docker-compose.yml
  start.bat
  stop.bat
```
