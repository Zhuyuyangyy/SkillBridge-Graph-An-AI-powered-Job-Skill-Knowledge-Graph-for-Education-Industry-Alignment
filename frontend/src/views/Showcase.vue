<template>
  <div class="showcase">
    <div class="sc-bg" aria-hidden="true">
      <span class="sc-aurora a"></span>
      <span class="sc-aurora b"></span>
      <span class="sc-grid"></span>
    </div>

    <!-- Top bar -->
    <header class="sc-topbar">
      <div class="sc-brand">
        <span class="sc-logo">SR</span>
        <div>
          <b>SkillBridge Graph · 数融智联</b>
          <small>岗位能力动态图谱与人岗对齐平台</small>
        </div>
      </div>
      <nav class="sc-nav">
        <a href="https://github.com/Zhuyuyangyy/SkillBridge-Graph-An-AI-powered-Job-Skill-Knowledge-Graph-for-Education-Industry-Alignment" target="_blank" rel="noreferrer">GitHub</a>
        <button class="sc-enter" @click="goApp">进入系统<el-icon><ArrowRight /></el-icon></button>
      </nav>
    </header>

    <!-- Hero -->
    <section class="sc-hero">
      <div class="sc-tag">AI-POWERED JOB · SKILL KNOWLEDGE GRAPH</div>
      <h1>让岗位能力<span class="grad">看得见、可追溯、能对齐</span></h1>
      <p class="sc-sub">
        面向教育与产业对齐场景，以多源岗位数据驱动
        <b>岗位发现 · 能力演化 · 图谱推理 · 人岗匹配 · 学习路径</b>
        的证据化闭环。每一个能力节点、每一次岗位更新、每一条匹配差距，都能回溯到真实来源。
      </p>
      <div class="sc-hero-actions">
        <button class="sc-cta primary" @click="goApp">立即体验<el-icon><ArrowRight /></el-icon></button>
        <button class="sc-cta ghost" @click="scrollTo('graph')">查看能力图谱</button>
      </div>
    </section>

    <!-- KPI value bar -->
    <section class="sc-kpis">
      <div v-for="k in kpis" :key="k.label" class="sc-kpi">
        <span class="sc-kpi__num">{{ k.value }}<i>{{ k.unit }}</i></span>
        <span class="sc-kpi__label">{{ k.label }}</span>
      </div>
    </section>

    <!-- Closed loop -->
    <section class="sc-section">
      <div class="sc-sec-head">
        <h2>赛题闭环</h2>
        <span>数据进入系统之后发生了什么</span>
      </div>
      <div class="sc-flow">
        <template v-for="(step, i) in flow" :key="step.t">
          <div class="sc-flow-node" :style="{ '--c': step.c }">
            <span class="sc-flow-idx">{{ String(i + 1).padStart(2, '0') }}</span>
            <b>{{ step.t }}</b>
            <small>{{ step.d }}</small>
          </div>
          <span v-if="i < flow.length - 1" class="sc-flow-arrow">→</span>
        </template>
      </div>
    </section>

    <!-- Graph + version -->
    <section id="graph" class="sc-section sc-two">
      <div class="sc-card sc-graph">
        <div class="sc-card-head"><h3>动态能力图谱</h3><span>{{ stats.nodeCount || 0 }} 节点 · {{ stats.edgeCount || 0 }} 关系 · {{ stats.communityCount || 0 }} 社区</span></div>
        <EChart :option="graphOption" style="height: 360px" />
      </div>
      <div class="sc-card sc-ver">
        <div class="sc-card-head"><h3>岗位能力版本演化</h3><span>可追溯的动态更新</span></div>
        <div v-if="verCard" class="sc-ver-card">
          <div class="sc-ver-top">
            <b>{{ verCard.jobName }}</b>
            <span class="sc-ver-badge">{{ verCard.fromVersion }} → {{ verCard.toVersion }}</span>
          </div>
          <div class="sc-ver-diff">
            <div class="sc-ver-col add"><span>新增</span><em v-for="s in verCard.added" :key="s">+ {{ s }}</em></div>
            <div class="sc-ver-col mod"><span>调整</span><em v-for="s in verCard.modified" :key="s.name">~ {{ s.name }}</em></div>
            <div class="sc-ver-col del"><span>淘汰</span><em v-for="s in verCard.removed" :key="s">− {{ s }}</em></div>
          </div>
          <div class="sc-ver-foot">证据置信度 {{ (verCard.confidence * 100).toFixed(0) }}% · 变更均带来源与审核记录</div>
        </div>
      </div>
    </section>

    <!-- Core innovation -->
    <section class="sc-section">
      <div class="sc-sec-head"><h2>核心创新</h2><span>不是"用了什么"，而是"解决了什么、凭什么可信"</span></div>
      <div class="sc-innov">
        <article v-for="(c, i) in innovations" :key="c.title" class="sc-innov-card" :style="{ '--c': c.color }">
          <span class="sc-innov-idx">0{{ i + 1 }}</span>
          <h4>{{ c.title }}</h4>
          <p>{{ c.desc }}</p>
        </article>
      </div>
    </section>

    <!-- Evidence + metrics -->
    <section class="sc-section sc-two">
      <div class="sc-card">
        <div class="sc-card-head"><h3>证据化与可信治理</h3><span>可解释 · 可追溯 · 可纠偏</span></div>
        <ul class="sc-evi-list">
          <li><b>来源可回溯</b>每个能力节点可展开真实 JD 语料来源片段、来源命中数与置信度。</li>
          <li><b>低置信度拦截</b>置信度不足或证据不够的内容进入人工审核，不直接写入正式图谱。</li>
          <li><b>版本可对比</b>岗位能力按版本记录新增 / 调整 / 淘汰，变更均带依据。</li>
        </ul>
      </div>
      <div class="sc-card">
        <div class="sc-card-head"><h3>可复现评测</h3><span>python -m app.evaluation.run_eval</span></div>
        <div class="sc-metric-grid">
          <div class="sc-metric"><span class="n">{{ overview.jd_parse_accuracy ?? '—' }}<i>%</i></span><span class="l">JD 解析准确率</span></div>
          <div class="sc-metric"><span class="n">{{ overview.resume_parse_accuracy ?? '—' }}<i>%</i></span><span class="l">简历解析准确率</span></div>
          <div class="sc-metric"><span class="n">{{ overview.match_accuracy ?? '—' }}<i>%</i></span><span class="l">人岗匹配准确率</span></div>
          <div class="sc-metric"><span class="n">{{ overview.unit_test_coverage ?? '—' }}<i>%</i></span><span class="l">单元测试覆盖</span></div>
        </div>
        <p class="sc-metric-note">一条命令复现三条能力的 precision / recall / f1、Top-1 准确率与错误案例。</p>
      </div>
    </section>

    <footer class="sc-footer">
      <div>
        <b>SkillBridge Graph · 数融智联</b>
        <span>Vue 3 + FastAPI + SQLAlchemy · 知识图谱 · 能力演化 · 人岗对齐</span>
      </div>
      <button class="sc-cta primary" @click="goApp">进入系统<el-icon><ArrowRight /></el-icon></button>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowRight } from '@element-plus/icons-vue'
import EChart from '@/components/EChart.vue'
import { api } from '@/api/http'

const router = useRouter()
const overview = ref<any>({})
const stats = ref<any>({})
const graphData = ref<{ nodes: any[]; edges: any[] }>({ nodes: [], edges: [] })
const verCard = ref<any>(null)

const kpis = computed(() => [
  { label: '多源岗位 JD', value: overview.value.jd_count ?? 0, unit: ' 条' },
  { label: '岗位 / 能力实体', value: `${overview.value.job_count ?? 0}/${overview.value.skill_count ?? 0}`, unit: '' },
  { label: '图谱关系边', value: overview.value.graph_relation_count ?? 0, unit: '' },
  { label: '新兴岗位发现', value: overview.value.emerging_job_count ?? 0, unit: '' },
  { label: '人岗匹配准确率', value: overview.value.match_accuracy ?? 0, unit: '%' },
  { label: '单元测试覆盖', value: overview.value.unit_test_coverage ?? 0, unit: '%' }
])

const flow = [
  { t: '多源采集', d: 'JD / 行业标准 / 课程', c: '#2563eb' },
  { t: '能力抽取', d: '证据约束 + 幻觉防护', c: '#0ea5e9' },
  { t: '图谱构建', d: '岗位-技能知识图谱', c: '#06b6d4' },
  { t: '动态演化', d: '版本化能力更新', c: '#14b8a6' },
  { t: '简历解析', d: '结构化画像', c: '#18b981' },
  { t: '匹配诊断', d: '差距 + 证据', c: '#f59e0b' },
  { t: '学习路径', d: '差距转行动', c: '#ec4899' },
  { t: '人工审核', d: '低置信度治理', c: '#7c3aed' },
  { t: '评测复现', d: '指标 + 错误案例', c: '#f43f5e' }
]

const innovations = [
  {
    title: '岗位能力下沉到技能级',
    desc: '把岗位能力从"岗位级标签"下沉到"技能级实体"，并做版本化、可追溯的动态演化，能一眼看出岗位新增、弱化、替代了什么能力及依据。',
    color: '#06b6d4'
  },
  {
    title: '大模型限制在证据与审核链条内',
    desc: '把大模型能力约束在证据引用和人工审核链条内，能展示误差、低置信度与人工纠偏，而不是"黑箱输出即结论"。',
    color: '#7c3aed'
  },
  {
    title: '解析-诊断-学习闭环对齐',
    desc: '把简历解析、能力差距诊断、学习路径推荐串成一条闭环，并给出准确率与错误案例，让"人岗对齐"可量化、可复现。',
    color: '#18b981'
  }
]

const graphOption = computed(() => {
  const nodes = graphData.value.nodes
  const ids = new Set(nodes.map((n) => n.id))
  const edges = graphData.value.edges.filter((e) => ids.has(e.source) && ids.has(e.target))
  return {
    tooltip: { trigger: 'item', formatter: (p: any) => (p.dataType === 'node' ? p.data.name : '') },
    series: [
      {
        type: 'graph',
        layout: 'force',
        roam: true,
        data: nodes.map((n) => ({
          id: n.id,
          name: n.label,
          symbolSize: Math.min(n.size, 40),
          itemStyle: { color: n.color, borderColor: 'rgba(255,255,255,0.5)', borderWidth: 1, shadowBlur: 14, shadowColor: `${n.color}66` }
        })),
        links: edges.map((e) => ({ source: e.source, target: e.target })),
        label: { show: true, color: '#cfe6ff', fontSize: 10, position: 'bottom', formatter: (p: any) => (p.data.name.length > 6 ? p.data.name.slice(0, 6) + '…' : p.data.name) },
        lineStyle: { color: 'rgba(150,190,255,0.28)', curveness: 0.1 },
        emphasis: { focus: 'adjacency', lineStyle: { color: 'rgba(120,220,255,0.7)', width: 2 } },
        force: { repulsion: 200, edgeLength: [50, 120], gravity: 0.1 }
      }
    ]
  }
})

function goApp() {
  router.push('/login')
}

function scrollTo(id: string) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
}

onMounted(async () => {
  try {
    const [ov, full, ver] = await Promise.all([
      api.overview(),
      api.graphFull({ limit: 64 }),
      api.evolutionVersionCompare()
    ])
    overview.value = ov
    stats.value = full?.stats ?? {}
    graphData.value = { nodes: full?.nodes ?? [], edges: full?.edges ?? [] }
    verCard.value = Array.isArray(ver?.cards) && ver.cards.length ? ver.cards[0] : null
  } catch {
    /* showcase degrades gracefully with empty data */
  }
})
</script>

<style scoped>
.showcase {
  position: relative;
  min-width: 0;
  min-height: 100vh;
  overflow-x: hidden;
  color: #e6f2ff;
  background: #060d1f;
  font-family: Inter, 'Microsoft YaHei', 'PingFang SC', 'Segoe UI', Arial, sans-serif;
}

.sc-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}

.sc-aurora {
  position: absolute;
  border-radius: 50%;
  filter: blur(90px);
  opacity: 0.5;
}

.sc-aurora.a {
  top: -120px;
  left: -80px;
  width: 460px;
  height: 460px;
  background: radial-gradient(circle, rgba(37, 99, 235, 0.6), transparent 70%);
}

.sc-aurora.b {
  top: 120px;
  right: -100px;
  width: 520px;
  height: 520px;
  background: radial-gradient(circle, rgba(6, 182, 212, 0.45), transparent 70%);
}

.sc-grid {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(rgba(120, 180, 255, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(120, 180, 255, 0.05) 1px, transparent 1px);
  background-size: 44px 44px;
  mask-image: radial-gradient(circle at 50% 30%, #000 30%, transparent 78%);
}

.showcase > *:not(.sc-bg) {
  position: relative;
  z-index: 1;
}

.sc-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1200px;
  margin: 0 auto;
  padding: 22px 24px;
}

.sc-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sc-logo {
  display: grid;
  place-items: center;
  width: 46px;
  height: 46px;
  border-radius: 14px;
  background: linear-gradient(135deg, #2563eb, #06b6d4);
  box-shadow: 0 0 26px rgba(6, 182, 212, 0.4);
  font-weight: 950;
  color: #fff;
}

.sc-brand b {
  display: block;
  font-size: 16px;
}

.sc-brand small {
  color: #8fb2d6;
  font-size: 12px;
}

.sc-nav {
  display: flex;
  align-items: center;
  gap: 18px;
}

.sc-nav a {
  color: #b8d4ef;
  font-weight: 700;
  font-size: 14px;
  text-decoration: none;
}

.sc-nav a:hover {
  color: #fff;
}

.sc-enter,
.sc-cta {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 0;
  border-radius: 12px;
  padding: 10px 18px;
  font-weight: 800;
  font-size: 14px;
  cursor: pointer;
  color: #fff;
  background: linear-gradient(135deg, #2563eb, #06b6d4);
  box-shadow: 0 10px 26px rgba(37, 99, 235, 0.35);
  transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease;
}

.sc-enter:hover,
.sc-cta.primary:hover {
  transform: translateY(-2px);
  filter: saturate(1.1);
}

.sc-hero {
  max-width: 980px;
  margin: 46px auto 10px;
  padding: 0 24px;
  text-align: center;
}

.sc-tag {
  display: inline-block;
  margin-bottom: 20px;
  border: 1px solid rgba(120, 200, 255, 0.3);
  border-radius: 999px;
  padding: 6px 16px;
  color: #7fe3ff;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.16em;
  background: rgba(80, 180, 255, 0.08);
}

.sc-hero h1 {
  margin: 0;
  font-size: 46px;
  font-weight: 950;
  line-height: 1.18;
  letter-spacing: 1px;
}

.grad {
  background: linear-gradient(120deg, #38bdf8, #22d3ee, #818cf8);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.sc-sub {
  max-width: 760px;
  margin: 22px auto 0;
  color: #a9c6e4;
  font-size: 16px;
  line-height: 1.8;
}

.sc-sub b {
  color: #d7ecff;
}

.sc-hero-actions {
  display: flex;
  justify-content: center;
  gap: 14px;
  margin-top: 30px;
}

.sc-cta {
  padding: 13px 26px;
  font-size: 15px;
}

.sc-cta.ghost {
  background: transparent;
  border: 1px solid rgba(120, 200, 255, 0.4);
  box-shadow: none;
  color: #cfe6ff;
}

.sc-cta.ghost:hover {
  background: rgba(80, 180, 255, 0.12);
}

.sc-kpis {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 14px;
  max-width: 1200px;
  margin: 50px auto 0;
  padding: 0 24px;
}

.sc-kpi {
  border: 1px solid rgba(120, 180, 255, 0.18);
  border-radius: 16px;
  padding: 18px 16px;
  background: linear-gradient(160deg, rgba(20, 40, 82, 0.7), rgba(9, 20, 44, 0.6));
  backdrop-filter: blur(10px);
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.sc-kpi:hover {
  transform: translateY(-3px);
  border-color: rgba(120, 220, 255, 0.5);
}

.sc-kpi__num {
  display: block;
  font-size: 30px;
  font-weight: 950;
  color: #eaf6ff;
  line-height: 1;
}

.sc-kpi__num i {
  font-size: 14px;
  font-style: normal;
  color: #7fb8e6;
}

.sc-kpi__label {
  display: block;
  margin-top: 10px;
  color: #8fb2d6;
  font-size: 13px;
  font-weight: 700;
}

.sc-section {
  max-width: 1200px;
  margin: 66px auto 0;
  padding: 0 24px;
}

.sc-sec-head {
  margin-bottom: 26px;
  text-align: center;
}

.sc-sec-head h2 {
  margin: 0;
  font-size: 30px;
  font-weight: 950;
}

.sc-sec-head span {
  display: block;
  margin-top: 10px;
  color: #8fb2d6;
  font-size: 15px;
}

.sc-flow {
  display: flex;
  flex-wrap: wrap;
  align-items: stretch;
  justify-content: center;
  gap: 8px;
}

.sc-flow-node {
  flex: 0 0 122px;
  width: 122px;
  border: 1px solid color-mix(in srgb, var(--c) 40%, transparent);
  border-radius: 14px;
  padding: 14px 12px;
  background: color-mix(in srgb, var(--c) 10%, rgba(10, 22, 46, 0.7));
  text-align: center;
}

.sc-flow-idx {
  display: inline-block;
  margin-bottom: 6px;
  color: var(--c);
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 1px;
}

.sc-flow-node b {
  display: block;
  font-size: 15px;
  color: #eaf6ff;
}

.sc-flow-node small {
  display: block;
  margin-top: 5px;
  color: #91b4d8;
  font-size: 11px;
}

.sc-flow-arrow {
  align-self: center;
  color: #4f6f9c;
  font-weight: 800;
}

.sc-two {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 20px;
}

.sc-card {
  border: 1px solid rgba(120, 180, 255, 0.18);
  border-radius: 20px;
  padding: 20px;
  background: linear-gradient(160deg, rgba(18, 36, 74, 0.66), rgba(9, 20, 44, 0.6));
  backdrop-filter: blur(12px);
}

.sc-card-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.sc-card-head h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 900;
}

.sc-card-head span {
  color: #7fb8e6;
  font-size: 12px;
  font-weight: 700;
}

.sc-ver-card {
  border: 1px solid rgba(120, 180, 255, 0.16);
  border-radius: 14px;
  padding: 16px;
  background: rgba(10, 24, 50, 0.5);
}

.sc-ver-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.sc-ver-top b {
  font-size: 16px;
}

.sc-ver-badge {
  border: 1px solid rgba(37, 99, 235, 0.5);
  border-radius: 8px;
  padding: 3px 10px;
  color: #7fc9ff;
  font-size: 12px;
  font-weight: 850;
}

.sc-ver-diff {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.sc-ver-col {
  border-radius: 12px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.03);
}

.sc-ver-col span {
  display: block;
  margin-bottom: 8px;
  font-size: 12px;
  font-weight: 850;
}

.sc-ver-col em {
  display: block;
  margin-bottom: 5px;
  font-style: normal;
  font-size: 13px;
  font-weight: 700;
}

.sc-ver-col.add span,
.sc-ver-col.add em {
  color: #34d399;
}

.sc-ver-col.mod span,
.sc-ver-col.mod em {
  color: #fbbf24;
}

.sc-ver-col.del span,
.sc-ver-col.del em {
  color: #fb7185;
}

.sc-ver-foot {
  margin-top: 14px;
  color: #7fb8e6;
  font-size: 12px;
  font-weight: 700;
}

.sc-innov {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}

.sc-innov-card {
  position: relative;
  border: 1px solid color-mix(in srgb, var(--c) 34%, transparent);
  border-radius: 18px;
  padding: 24px 20px;
  background: linear-gradient(160deg, color-mix(in srgb, var(--c) 12%, rgba(12, 26, 52, 0.7)), rgba(9, 20, 44, 0.6));
  overflow: hidden;
}

.sc-innov-card::before {
  content: '';
  position: absolute;
  top: -30px;
  right: -30px;
  width: 90px;
  height: 90px;
  border-radius: 50%;
  background: var(--c);
  filter: blur(46px);
  opacity: 0.4;
}

.sc-innov-idx {
  color: var(--c);
  font-size: 26px;
  font-weight: 950;
}

.sc-innov-card h4 {
  margin: 10px 0 12px;
  font-size: 18px;
  font-weight: 900;
}

.sc-innov-card p {
  margin: 0;
  color: #a9c6e4;
  font-size: 14px;
  line-height: 1.8;
}

.sc-evi-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.sc-evi-list li {
  position: relative;
  margin-bottom: 14px;
  padding-left: 20px;
  color: #a9c6e4;
  font-size: 14px;
  line-height: 1.7;
}

.sc-evi-list li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 8px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: linear-gradient(135deg, #22d3ee, #818cf8);
  box-shadow: 0 0 10px rgba(34, 211, 238, 0.7);
}

.sc-evi-list b {
  display: block;
  color: #eaf6ff;
  font-size: 14px;
}

.sc-metric-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.sc-metric {
  border: 1px solid rgba(120, 180, 255, 0.16);
  border-radius: 14px;
  padding: 14px;
  text-align: center;
  background: rgba(10, 24, 50, 0.5);
}

.sc-metric .n {
  display: block;
  font-size: 26px;
  font-weight: 950;
  color: #7fe3ff;
}

.sc-metric .n i {
  font-size: 13px;
  font-style: normal;
}

.sc-metric .l {
  display: block;
  margin-top: 6px;
  color: #8fb2d6;
  font-size: 12px;
  font-weight: 700;
}

.sc-metric-note {
  margin: 14px 0 0;
  color: #7fb8e6;
  font-size: 13px;
}

.sc-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1200px;
  margin: 70px auto 0;
  padding: 28px 24px 50px;
  border-top: 1px solid rgba(120, 180, 255, 0.14);
}

.sc-footer b {
  display: block;
  font-size: 16px;
}

.sc-footer span {
  color: #8fb2d6;
  font-size: 13px;
}

@media (max-width: 1080px) {
  .sc-kpis {
    grid-template-columns: repeat(3, 1fr);
  }
  .sc-two {
    grid-template-columns: 1fr;
  }
  .sc-innov {
    grid-template-columns: 1fr;
  }
  .sc-hero h1 {
    font-size: 34px;
  }
}
</style>
