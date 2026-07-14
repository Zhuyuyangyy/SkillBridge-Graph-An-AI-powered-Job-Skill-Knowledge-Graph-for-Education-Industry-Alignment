<template>
  <div class="showcase">
    <!-- 顶部标题区 -->
    <header class="showcase-hero">
      <div class="hero-inner">
        <div class="hero-kicker">挑战杯 · 项目展示</div>
        <h1>SkillBridge Graph 岗位能力动态图谱与人岗对齐平台</h1>
        <p>多源岗位数据驱动的岗位发现、能力演化、匹配与学习闭环</p>
        <div class="hero-actions">
          <el-button type="primary" size="large" @click="enter">进入系统</el-button>
          <el-button size="large" @click="$router.push('/login')">登录后台</el-button>
        </div>
      </div>
      <div class="hero-orbit">
        <div class="orbit ring-1"></div>
        <div class="orbit ring-2"></div>
        <div class="orbit core"><span>{{ kpi.skillCount }}</span><b>技能实体</b></div>
      </div>
    </header>

    <!-- KPI 条 -->
    <section class="kpi-row">
      <article v-for="k in kpis" :key="k.label" class="kpi-card">
        <span class="kpi-label">{{ k.label }}</span>
        <strong class="kpi-value">{{ k.value }}</strong>
        <small class="kpi-desc">{{ k.desc }}</small>
      </article>
    </section>

    <!-- 闭环流程 -->
    <section class="panel">
      <div class="panel-head"><div><span>赛题闭环流程</span><small>CLOSED LOOP</small></div></div>
      <div class="flow-lane">
        <div v-for="(s, i) in flow" :key="s.title" class="flow-step" @click="enter(s.path)">
          <span class="flow-no">{{ String(i + 1).padStart(2, '0') }}</span>
          <b>{{ s.title }}</b>
          <small>{{ s.desc }}</small>
          <i v-if="i < flow.length - 1" class="flow-arrow">→</i>
        </div>
      </div>
    </section>

    <div class="content-grid">
      <!-- 中间：能力网络 -->
      <section class="panel span-7">
        <div class="panel-head"><div><span>能力网络大脑</span><small>SKILL GRAPH</small></div>
          <el-tag effect="light" type="primary">{{ kpi.communityCount }} 个领域社区</el-tag>
        </div>
        <div ref="graphRef" class="mini-graph"></div>
        <div class="hub-list">
          <span class="hub-label">核心枢纽岗位</span>
          <el-tag v-for="h in hubs" :key="h.label" effect="plain" type="primary" style="margin: 3px">{{ h.label }} · {{ h.degree }}</el-tag>
        </div>
      </section>

      <!-- 右侧：证据链与落地 -->
      <aside class="span-5">
        <section class="panel evi-panel">
          <div class="panel-head"><div><span>证据链与可信治理</span><small>EVIDENCE</small></div></div>
          <p class="evi-desc">每个技能节点、岗位变化、匹配差距均可展开查看：来源片段、来源数量、置信度、审核状态与更新时间，可解释、可追溯。</p>
          <div class="evi-mock">
            <div class="evi-row"><span>置信度</span><el-progress :percentage="91" :stroke-width="8" /></div>
            <div class="evi-row"><span>来源命中</span><b>10 条 JD 语料</b></div>
            <div class="evi-row"><span>审核状态</span><el-tag size="small" type="success" effect="light">已入图谱</el-tag></div>
          </div>
        </section>

        <section class="panel version-panel">
          <div class="panel-head"><div><span>岗位能力版本对比</span><small>VERSION DIFF</small></div></div>
          <div class="ver-card">
            <div class="ver-top"><b>Java 开发工程师</b><span class="ver-badge">v2024 → v2026</span></div>
            <div class="ver-diff">
              <div class="vd add"><span>新增</span><el-tag size="small" type="success" effect="light">RAG</el-tag><el-tag size="small" type="success" effect="light">向量数据库</el-tag></div>
              <div class="vd del"><span>淘汰</span><el-tag size="small" type="danger" effect="light">JSP</el-tag></div>
              <div class="vd mod"><span>调整</span><el-tag size="small" type="warning" effect="light">Spring→Spring Boot 3</el-tag></div>
            </div>
          </div>
        </section>
      </aside>
    </div>

    <!-- 真实样本与数据源 -->
    <section class="panel">
      <div class="panel-head"><div><span>真实样本与数据来源</span><small>DATA SOURCES</small></div></div>
      <div class="source-grid">
        <div v-for="d in sources" :key="d.title" class="source-card">
          <span class="source-icon">{{ d.icon }}</span>
          <b>{{ d.title }}</b>
          <small>{{ d.desc }}</small>
        </div>
      </div>
    </section>

    <footer class="showcase-foot">
      <span>数融智联 · 岗位能力图谱构建与分析系统（融合 JobGraph 图谱能力）</span>
      <el-button text type="primary" @click="enter">查看完整系统 →</el-button>
    </footer>
  </div>
</template>

<script setup lang="ts">
import * as echarts from 'echarts'
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api/http'

const router = useRouter()
const graphRef = ref<HTMLDivElement>()
const overview = ref<any>({})
const graphStats = ref<any>({})
const evaluation = ref<any>({})
let chart: echarts.ECharts | undefined

const kpi = computed(() => ({
  jdCount: overview.value.jd_count ?? 0,
  emergingJobCount: overview.value.emerging_job_count ?? 0,
  evolutionEventCount: overview.value.evolution_event_count ?? 0,
  skillCount: overview.value.skill_count ?? 0,
  communityCount: graphStats.value.communityCount ?? 0,
  jdF1: evaluation.value.jd_parse_accuracy ?? 0,
  matchAcc: evaluation.value.match_accuracy ?? 0
}))

const kpis = computed(() => [
  { label: 'JD 样本', value: kpi.value.jdCount, desc: '已入库岗位文本' },
  { label: '新发现岗位', value: kpi.value.emergingJobCount, desc: '多源一致性识别' },
  { label: '能力变更数', value: kpi.value.evolutionEventCount, desc: '动态演化事件' },
  { label: 'JD 抽取 F1', value: `${kpi.value.jdF1}%`, desc: '可复现评测' },
  { label: '匹配 Top-1', value: `${kpi.value.matchAcc}%`, desc: '人岗匹配准确率' },
  { label: '技能实体', value: kpi.value.skillCount, desc: '可检索能力项' }
])

const flow = [
  { title: '数据采集', desc: '多源 JD 入库与质量评估', path: '/datasets' },
  { title: '能力抽取', desc: 'JD/简历技能结构化', path: '/jd-parser' },
  { title: '能力图谱', desc: '社区聚类与核心枢纽', path: '/graph-explore' },
  { title: '人岗匹配', desc: '差距诊断与证据', path: '/match-analysis' },
  { title: '学习路径', desc: '差距翻译为行动', path: '/learning-path' },
  { title: '可信审核', desc: '低置信度治理', path: '/review-tasks' },
  { title: '一键评测', desc: '可复现指标与错误案例', path: '/evaluation' }
]

const hubs = computed(() => (graphStats.value.topHubs || []).slice(0, 6))

const sources = [
  { icon: '📄', title: '招聘平台样本', desc: '120+ JD 真实语料' },
  { icon: '🏛', title: '企业官网岗位页', desc: '一手岗位描述' },
  { icon: '📊', title: '行业报告与白皮书', desc: '能力趋势校准' },
  { icon: '🎓', title: '校招数据集', desc: '岗位-课程对齐' }
]

function enter(path?: string) {
  const token = localStorage.getItem('auth_token')
  router.push(token ? (path || '/overview') : '/login').catch(() => undefined)
}

function renderMini() {
  if (!graphRef.value) return
  chart ??= echarts.init(graphRef.value)
  // 用力导向图表达“能力网络”示意（不依赖登录态接口）
  const palette = ['#2563eb', '#06b6d4', '#7c3aed', '#18b981', '#f59e0b', '#ec4899']
  const nodes = [
    '后端开发', 'Java', 'Python', 'Spring', 'MySQL', 'Redis', 'Docker',
    '数据开发', 'Spark', 'Kafka', 'AI 工程', 'RAG', '向量数据库', 'Prompt'
  ].map((name, i) => ({
    name,
    symbolSize: 18 + (i % 4) * 8,
    itemStyle: { color: palette[i % palette.length] },
    label: { show: true, color: '#173665', fontSize: 11, fontWeight: 600 }
  }))
  const links = [
    ['后端开发', 'Java'], ['后端开发', 'Python'], ['后端开发', 'Spring'],
    ['Java', 'Spring'], ['Spring', 'MySQL'], ['后端开发', 'Redis'], ['后端开发', 'Docker'],
    ['数据开发', 'Python'], ['数据开发', 'Spark'], ['数据开发', 'Kafka'], ['Spark', 'MySQL'],
    ['AI 工程', 'Python'], ['AI 工程', 'RAG'], ['AI 工程', '向量数据库'], ['AI 工程', 'Prompt'],
    ['RAG', '向量数据库'], ['数据开发', 'AI 工程']
  ].map(([s, t]) => ({ source: s, target: t }))
  chart.setOption({
    animationDuration: 900,
    series: [{
      type: 'graph', layout: 'force', roam: false, draggable: false,
      data: nodes, links,
      lineStyle: { color: '#9fc1f0', width: 1, curveness: 0.1, opacity: 0.6 },
      force: { repulsion: 220, edgeLength: [50, 110], gravity: 0.12 }
    }]
  })
}

onMounted(async () => {
  const token = localStorage.getItem('auth_token')
  // 这些接口为公开接口，未登录也可展示
  try { overview.value = await api.overview() } catch { /* ignore */ }
  try { graphStats.value = await api.graphStats() } catch { /* ignore */ }
  try { evaluation.value = await api.evaluation() } catch { /* ignore */ }
  void token
  await nextTick()
  renderMini()
  window.addEventListener('resize', resize)
})

function resize() { chart?.resize() }

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  chart?.dispose()
})
</script>

<style scoped>
.showcase {
  min-width: 1180px;
  max-width: 1400px;
  margin: 0 auto;
  padding: 28px 32px 48px;
}

.showcase-hero {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 24px;
  overflow: hidden;
  min-height: 240px;
  border: 1px solid var(--border);
  border-radius: 24px;
  padding: 36px 38px;
  background:
    radial-gradient(circle at 14% 0%, rgba(6, 182, 212, 0.18), transparent 30%),
    radial-gradient(circle at 88% 16%, rgba(47, 94, 224, 0.16), transparent 30%),
    linear-gradient(135deg, var(--glass), rgba(232, 242, 255, 0.7));
  box-shadow: var(--shadow-lg);
  backdrop-filter: blur(20px);
}

.hero-kicker {
  display: inline-block;
  border: 1px solid rgba(6, 182, 212, 0.3);
  border-radius: 999px;
  padding: 6px 12px;
  background: var(--cyan-soft);
  color: var(--cyan);
  font-size: 12px;
  font-weight: 900;
}

.showcase-hero h1 {
  max-width: 720px;
  margin: 16px 0 10px;
  color: var(--heading);
  font-size: 30px;
  font-weight: 950;
  line-height: 1.25;
}

.showcase-hero p {
  margin: 0;
  color: var(--muted);
  font-size: 15px;
  font-weight: 650;
}

.hero-actions {
  display: flex;
  gap: 12px;
  margin-top: 22px;
}

.hero-orbit {
  position: relative;
  min-height: 220px;
}

.orbit {
  position: absolute;
  left: 50%;
  top: 50%;
  border-radius: 50%;
  transform: translate(-50%, -50%);
}

.ring-1 {
  width: 220px;
  height: 220px;
  border: 1px solid rgba(47, 94, 224, 0.22);
}

.ring-2 {
  width: 156px;
  height: 156px;
  border: 1px dashed rgba(6, 182, 212, 0.42);
  animation: spin 14s linear infinite;
}

.core {
  display: grid;
  place-items: center;
  width: 120px;
  height: 120px;
  border: 1px solid rgba(255, 255, 255, 0.9);
  background: linear-gradient(135deg, var(--primary), var(--cyan));
  box-shadow: 0 0 40px rgba(6, 182, 212, 0.32);
  color: #fff;
}

.core span { font-size: 32px; font-weight: 950; line-height: 1; }
.core b { margin-top: -22px; font-size: 12px; }

@keyframes spin { to { transform: translate(-50%, -50%) rotate(360deg); } }

.kpi-row {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 14px;
  margin: 18px 0;
}

.kpi-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 16px;
  background: var(--surface);
  box-shadow: var(--shadow-sm);
  transition: transform 200ms ease, box-shadow 200ms ease;
}

.kpi-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow);
}

.kpi-label {
  color: var(--muted);
  font-size: 12px;
  font-weight: 850;
}

.kpi-value {
  color: var(--heading);
  font-size: 28px;
  font-weight: 950;
}

.kpi-desc {
  color: var(--muted);
  font-size: 11px;
  font-weight: 700;
}

.panel {
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 20px;
  margin-bottom: 16px;
  background: var(--surface);
  box-shadow: var(--shadow-sm);
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.panel-head span {
  color: var(--text);
  font-size: 16px;
  font-weight: 900;
}

.panel-head small {
  margin-left: 8px;
  color: var(--cyan);
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.14em;
}

.flow-lane {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 10px;
}

.flow-step {
  position: relative;
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 14px 12px;
  background: var(--surface-2);
  cursor: pointer;
  transition: all 180ms ease;
}

.flow-step:hover {
  border-color: rgba(6, 182, 212, 0.45);
  background: var(--cyan-soft);
  transform: translateY(-2px);
}

.flow-no {
  display: inline-grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border-radius: 9px;
  background: linear-gradient(135deg, rgba(47, 94, 224, 0.14), rgba(6, 182, 212, 0.16));
  color: var(--primary);
  font-size: 11px;
  font-weight: 950;
}

.flow-step b {
  display: block;
  margin-top: 10px;
  color: var(--heading);
  font-size: 14px;
  font-weight: 900;
}

.flow-step small {
  display: block;
  margin-top: 5px;
  color: var(--muted);
  font-size: 11px;
  font-weight: 700;
  line-height: 1.5;
}

.flow-arrow {
  position: absolute;
  right: -10px;
  top: 50%;
  z-index: 2;
  color: var(--border-strong);
  font-style: normal;
  font-weight: 900;
  transform: translateY(-50%);
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: 16px;
}

.span-7 { grid-column: span 7; }
.span-5 { grid-column: span 5; }

.mini-graph {
  height: 280px;
  border: 1px solid rgba(47, 99, 235, 0.18);
  border-radius: 14px;
  background:
    radial-gradient(circle at 20% 12%, rgba(6, 182, 212, 0.1), transparent 30%),
    var(--surface-2);
}

.hub-list {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  margin-top: 12px;
}

.hub-label {
  color: var(--muted);
  font-size: 12px;
  font-weight: 850;
  margin-right: 6px;
}

.evi-desc {
  margin: 0 0 12px;
  color: var(--muted);
  font-size: 13px;
  line-height: 1.7;
}

.evi-mock {
  display: grid;
  gap: 10px;
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 14px;
  background: var(--surface-2);
}

.evi-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.evi-row span {
  color: var(--muted);
  font-size: 12px;
  font-weight: 850;
  flex: 0 0 72px;
}

.evi-row .el-progress { flex: 1; }
.evi-row b { color: var(--heading); font-size: 13px; }

.version-panel { margin-top: 14px; }

.ver-card {
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 14px;
  background: var(--surface-2);
}

.ver-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.ver-top b { color: var(--heading); font-size: 15px; }
.ver-badge {
  border: 1px solid rgba(47, 94, 224, 0.4);
  border-radius: 8px;
  padding: 3px 9px;
  background: var(--primary-soft);
  color: var(--primary);
  font-size: 11px;
  font-weight: 850;
}

.ver-diff { display: grid; gap: 10px; }
.vd { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.vd span { color: var(--muted); font-size: 12px; font-weight: 850; flex: 0 0 44px; }

.source-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.source-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 16px;
  background: var(--surface-2);
  transition: transform 180ms ease;
}

.source-card:hover { transform: translateY(-2px); }

.source-icon { font-size: 22px; }
.source-card b { color: var(--heading); font-size: 14px; }
.source-card small { color: var(--muted); font-size: 12px; font-weight: 700; }

.showcase-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 20px;
  padding: 16px 4px 0;
  border-top: 1px solid var(--border);
  color: var(--muted);
  font-size: 13px;
  font-weight: 700;
}
</style>
