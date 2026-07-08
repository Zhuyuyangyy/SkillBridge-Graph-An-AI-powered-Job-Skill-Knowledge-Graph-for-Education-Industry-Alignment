<template>
  <div class="page graph-explore-page">
    <PageHeader title="图谱探索" desc="社区聚类、核心枢纽与技能迁移路径分析">
      <el-input
        v-model="keyword"
        clearable
        placeholder="搜索岗位或技能"
        style="width: 220px"
        @input="applyFilter"
      >
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <el-select v-model="activeCommunity" clearable placeholder="全部社区" style="width: 168px" @change="applyFilter">
        <el-option v-for="c in communities" :key="c.index" :label="c.name" :value="c.index">
          <span class="opt-dot" :style="{ background: c.color }"></span>{{ c.name }}
        </el-option>
      </el-select>
      <el-button :loading="loading" @click="resetView">重置视图</el-button>
      <el-button type="primary" :loading="loading" @click="loadData">刷新图谱</el-button>
    </PageHeader>

    <div class="metric-grid graph-metrics">
      <div v-for="m in metricCards" :key="m.label" class="metric-card">
        <div class="metric-label">{{ m.label }}</div>
        <div class="metric-value">{{ m.value }}</div>
      </div>
    </div>

    <div class="content-grid">
      <!-- Graph stage -->
      <section class="panel span-8 graph-panel">
        <div class="panel-heading">
          <div>
            <span>能力网络</span>
            <small>FORCE-DIRECTED GRAPH</small>
          </div>
          <div class="legend">
            <span v-for="c in communities.slice(0, 6)" :key="c.index" class="legend-item">
              <i :style="{ background: c.color }"></i>{{ c.name }}
            </span>
          </div>
        </div>
        <div v-loading="loading" class="graph-stage">
          <div ref="containerRef" class="graph-box"></div>
          <div v-if="!loading && !visibleNodes.length" class="graph-message">
            <el-empty description="没有符合条件的节点" />
          </div>
        </div>
      </section>

      <!-- Side analytics -->
      <aside class="span-4 graph-side">
        <section class="panel side-block">
          <div class="panel-heading"><div><span>社区分布</span><small>COMMUNITY</small></div></div>
          <div class="comm-list">
            <button
              v-for="c in communities"
              :key="c.index"
              class="comm-row"
              :class="{ active: activeCommunity === c.index }"
              @click="toggleCommunity(c.index)"
            >
              <span class="comm-dot" :style="{ background: c.color }"></span>
              <span class="comm-name">{{ c.name }}</span>
              <span class="comm-count">{{ c.count }}</span>
              <span class="comm-bar"><i :style="{ width: barWidth(c.count), background: c.color }"></i></span>
            </button>
          </div>
        </section>

        <section class="panel side-block">
          <div class="panel-heading"><div><span>技能迁移路径</span><small>CAREER PATH</small></div></div>
          <el-select v-model="pathFrom" filterable placeholder="起始岗位" class="path-select">
            <el-option v-for="j in jobOptions" :key="j.value" :label="j.label" :value="j.value" />
          </el-select>
          <el-select v-model="pathTo" filterable placeholder="目标岗位" class="path-select">
            <el-option v-for="j in jobOptions" :key="j.value" :label="j.label" :value="j.value" />
          </el-select>
          <el-button type="primary" style="width: 100%" :disabled="!pathFrom || !pathTo" :loading="pathLoading" @click="findPath">
            分析迁移路径
          </el-button>
          <div v-if="pathResult" class="path-result">
            <template v-if="pathResult.found">
              <div class="path-chain">
                <template v-for="(n, i) in pathResult.path" :key="i">
                  <span class="path-node" :class="n.type">{{ n.label }}</span>
                  <span v-if="i < pathResult.path.length - 1" class="path-arrow">→</span>
                </template>
              </div>
              <div v-if="pathResult.shared.length" class="path-shared">
                <span class="path-shared__label">可直接迁移能力</span>
                <el-tag v-for="s in pathResult.shared.slice(0, 8)" :key="s" size="small" effect="light" type="success">{{ s }}</el-tag>
              </div>
            </template>
            <el-empty v-else description="两个岗位之间暂无连通路径" :image-size="70" />
          </div>
        </section>

        <section class="panel side-block">
          <div class="panel-heading"><div><span>节点详情</span><small>NODE DETAIL</small></div></div>
          <el-empty v-if="!selected" description="点击图谱节点查看详情" :image-size="70" />
          <template v-else>
            <div class="selected-node" :style="{ '--node-color': selected.color }">
              <span class="selected-node__dot"></span>
              <div>
                <h3>{{ selected.label }}</h3>
                <el-tag effect="plain" :type="selected.type === 'job' ? 'primary' : 'success'">
                  {{ selected.type === 'job' ? '岗位' : '技能' }}
                </el-tag>
                <el-tag v-if="selected.isEmerging" effect="dark" type="warning" style="margin-left: 6px">新兴</el-tag>
              </div>
            </div>
            <div class="detail-block"><span>所属社区</span><p>{{ selected.communityName }}</p></div>
            <div class="detail-block"><span>中心度</span>
              <p><el-progress :percentage="Math.round(selected.centrality * 100)" :stroke-width="8" /></p>
            </div>
            <div class="detail-block"><span>关联关系</span><p>{{ selected.degree }} 条</p></div>
            <div v-if="selected.category" class="detail-block"><span>能力分类</span><p>{{ selected.category }}</p></div>
            <div class="detail-block"><span>证据来源</span><p>{{ selected.evidence || '已进入图谱，暂未补充来源说明。' }}</p></div>
          </template>
        </section>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import * as echarts from 'echarts'
import { Search } from '@element-plus/icons-vue'
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import { api } from '@/api/http'

type GraphNode = {
  id: string
  label: string
  type: string
  community: number
  communityName: string
  color: string
  degree: number
  centrality: number
  category?: string
  isEmerging?: boolean
  size: number
  evidence?: string
}
type GraphEdge = { source: string; target: string; weight: number; relation: string }
type Community = { index: number; name: string; color: string; count: number }

const containerRef = ref<HTMLDivElement>()
const allNodes = ref<GraphNode[]>([])
const allEdges = ref<GraphEdge[]>([])
const communities = ref<Community[]>([])
const stats = ref<any>({})
const keyword = ref('')
const activeCommunity = ref<number | null>(null)
const selected = ref<GraphNode | null>(null)
const loading = ref(false)
const pathFrom = ref<number | null>(null)
const pathTo = ref<number | null>(null)
const pathLoading = ref(false)
const pathResult = ref<{ found: boolean; path: { label: string; type: string }[]; shared: string[] } | null>(null)
let chart: echarts.ECharts | undefined
let resizeObserver: ResizeObserver | undefined

const metricCards = computed(() => [
  { label: '总节点', value: stats.value.nodeCount ?? 0 },
  { label: '岗位数', value: stats.value.jobCount ?? 0 },
  { label: '能力数', value: stats.value.skillCount ?? 0 },
  { label: '关系边', value: stats.value.edgeCount ?? 0 },
  { label: '社区数', value: stats.value.communityCount ?? 0 },
  { label: '平均度', value: stats.value.avgDegree ?? 0 }
])

const maxCount = computed(() => Math.max(1, ...communities.value.map((c) => c.count)))
const jobOptions = computed(() =>
  allNodes.value
    .filter((n) => n.type === 'job')
    .map((n) => ({ label: n.label, value: Number(n.id.replace('job-', '')) }))
)

const visibleNodes = computed(() => {
  let nodes = allNodes.value
  if (activeCommunity.value !== null) nodes = nodes.filter((n) => n.community === activeCommunity.value)
  const kw = keyword.value.trim().toLowerCase()
  if (kw) nodes = nodes.filter((n) => n.label.toLowerCase().includes(kw))
  return nodes
})

function barWidth(count: number) {
  return `${Math.round((count / maxCount.value) * 100)}%`
}

function toggleCommunity(index: number) {
  activeCommunity.value = activeCommunity.value === index ? null : index
  applyFilter()
}

function renderGraph() {
  const container = containerRef.value
  if (!container) return
  const nodes = visibleNodes.value
  const ids = new Set(nodes.map((n) => n.id))
  const edges = allEdges.value.filter((e) => ids.has(e.source) && ids.has(e.target))
  chart ??= echarts.init(container)
  if (!nodes.length) {
    chart.clear()
    return
  }
  chart.setOption(
    {
      animationDuration: 800,
      animationDurationUpdate: 450,
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(10, 40, 91, 0.92)',
        borderColor: 'rgba(133, 210, 255, 0.45)',
        textStyle: { color: '#eff9ff' },
        formatter: (p: any) => {
          if (p.dataType === 'edge') return `关联权重 ${(p.data.weight * 100).toFixed(0)}%`
          const n = p.data.raw as GraphNode
          return `<b>${n.label}</b><br/>${n.type === 'job' ? '岗位' : '技能'} · ${n.communityName}<br/>关联 ${n.degree} 条`
        }
      },
      series: [
        {
          type: 'graph',
          layout: 'force',
          roam: true,
          draggable: true,
          data: nodes.map((n) => ({
            id: n.id,
            name: n.label,
            raw: n,
            symbolSize: n.size,
            itemStyle: {
              color: n.color,
              borderColor: n.type === 'job' ? '#ffffff' : 'rgba(255,255,255,0.7)',
              borderWidth: n.type === 'job' ? 2.6 : 1.6,
              shadowBlur: 18,
              shadowColor: `${n.color}55`
            }
          })),
          links: edges.map((e) => ({
            source: e.source,
            target: e.target,
            weight: e.weight,
            lineStyle: { width: 0.6 + e.weight * 2.2 }
          })),
          categories: [],
          label: {
            show: true,
            position: 'bottom',
            distance: 6,
            color: '#173665',
            fontSize: 11,
            fontWeight: 600,
            formatter: (p: any) => (p.data.name.length > 9 ? `${p.data.name.slice(0, 9)}…` : p.data.name)
          },
          lineStyle: { color: 'source', opacity: 0.32, curveness: 0.1 },
          emphasis: {
            focus: 'adjacency',
            scale: 1.1,
            lineStyle: { opacity: 0.9, width: 2.4 },
            label: { fontSize: 13, fontWeight: 800 }
          },
          force: { repulsion: 320, edgeLength: [70, 160], gravity: 0.09, friction: 0.5, layoutAnimation: true }
        }
      ]
    },
    true
  )
  chart.off('click')
  chart.on('click', (p: any) => {
    if (p.dataType === 'node') selected.value = p.data.raw
  })
}

async function applyFilter() {
  await nextTick()
  renderGraph()
}

async function loadData() {
  loading.value = true
  try {
    const data = await api.graphFull({ limit: 400 })
    allNodes.value = Array.isArray(data?.nodes) ? data.nodes : []
    allEdges.value = Array.isArray(data?.edges) ? data.edges : []
    communities.value = Array.isArray(data?.communities) ? data.communities : []
    stats.value = data?.stats ?? {}
    if (selected.value && !allNodes.value.some((n) => n.id === selected.value?.id)) selected.value = null
    await nextTick()
    renderGraph()
  } finally {
    loading.value = false
  }
}

async function findPath() {
  if (!pathFrom.value || !pathTo.value) return
  pathLoading.value = true
  try {
    pathResult.value = await api.graphPath(pathFrom.value, pathTo.value)
  } finally {
    pathLoading.value = false
  }
}

function resetView() {
  keyword.value = ''
  activeCommunity.value = null
  pathResult.value = null
  pathFrom.value = null
  pathTo.value = null
  selected.value = null
  applyFilter()
}

onMounted(async () => {
  await loadData()
  if (containerRef.value) {
    resizeObserver = new ResizeObserver(() => chart?.resize())
    resizeObserver.observe(containerRef.value)
  }
})

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  chart?.dispose()
})
</script>

<style scoped>
.graph-explore-page {
  min-width: 0;
}

.opt-dot,
.comm-dot {
  display: inline-block;
  width: 9px;
  height: 9px;
  margin-right: 8px;
  border-radius: 50%;
  box-shadow: 0 0 8px currentColor;
}

.graph-metrics {
  grid-template-columns: repeat(6, minmax(0, 1fr));
}

.graph-metrics .metric-card {
  min-height: 96px;
  padding: 14px 16px;
}

.graph-metrics .metric-card::before {
  display: none;
}

.graph-metrics .metric-value {
  margin-top: 8px;
  font-size: 26px;
}

.graph-metrics .metric-value::after {
  margin-top: 8px;
  width: 40px;
}

.panel-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.panel-heading span {
  color: var(--text);
  font-size: 16px;
  font-weight: 900;
}

.panel-heading small {
  margin-left: 8px;
  color: var(--cyan);
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.14em;
}

.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 12px;
  justify-content: flex-end;
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  color: var(--muted);
  font-size: 11px;
  font-weight: 700;
}

.legend-item i {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  box-shadow: 0 0 8px currentColor;
}

.graph-stage {
  position: relative;
  min-height: 592px;
}

.graph-box {
  height: 592px;
  overflow: hidden;
  border: 1px solid rgba(37, 99, 235, 0.24);
  border-radius: 16px;
  background:
    linear-gradient(rgba(37, 99, 235, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(37, 99, 235, 0.05) 1px, transparent 1px),
    radial-gradient(circle at 18% 10%, rgba(6, 182, 212, 0.16), transparent 28%),
    linear-gradient(135deg, rgba(248, 251, 255, 0.9), rgba(231, 244, 255, 0.78));
  background-size: 34px 34px, 34px 34px, auto, auto;
  box-shadow: inset 0 0 46px rgba(6, 182, 212, 0.08);
}

.graph-message {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
}

.graph-side {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.side-block {
  padding: 18px;
}

.comm-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.comm-row {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 8px;
  border: 1px solid transparent;
  border-radius: 12px;
  padding: 8px 10px;
  background: transparent;
  color: var(--text);
  cursor: pointer;
  transition: all 0.2s ease;
}

.comm-row:hover,
.comm-row.active {
  border-color: rgba(6, 182, 212, 0.32);
  background: rgba(6, 182, 212, 0.08);
}

.comm-name {
  font-size: 13px;
  font-weight: 750;
}

.comm-count {
  color: var(--muted);
  font-size: 12px;
  font-weight: 800;
}

.comm-bar {
  grid-column: 1 / -1;
  height: 4px;
  border-radius: 99px;
  background: rgba(190, 213, 242, 0.42);
  overflow: hidden;
}

.comm-bar i {
  display: block;
  height: 100%;
  border-radius: 99px;
}

.path-select {
  width: 100%;
  margin-bottom: 10px;
}

.path-result {
  margin-top: 14px;
}

.path-chain {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
}

.path-node {
  border-radius: 10px;
  padding: 5px 10px;
  font-size: 12px;
  font-weight: 800;
}

.path-node.job {
  border: 1px solid rgba(37, 99, 235, 0.32);
  background: rgba(37, 99, 235, 0.1);
  color: var(--primary);
}

.path-node.skill {
  border: 1px solid rgba(24, 185, 129, 0.32);
  background: rgba(24, 185, 129, 0.1);
  color: var(--green);
}

.path-arrow {
  color: var(--muted);
  font-weight: 800;
}

.path-shared {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  margin-top: 12px;
}

.path-shared__label {
  width: 100%;
  color: var(--muted);
  font-size: 12px;
  font-weight: 800;
}

.selected-node {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  border: 1px solid rgba(78, 154, 255, 0.22);
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(230, 244, 255, 0.7), rgba(255, 255, 255, 0.5));
}

.selected-node h3 {
  margin: 0 0 7px;
  color: var(--text);
}

.selected-node__dot {
  flex: 0 0 auto;
  width: 18px;
  height: 18px;
  border: 5px solid rgba(255, 255, 255, 0.92);
  border-radius: 50%;
  background: var(--node-color);
  box-shadow: 0 0 0 5px color-mix(in srgb, var(--node-color) 18%, transparent), 0 0 18px var(--node-color);
}

.detail-block {
  padding: 13px 2px;
  border-bottom: 1px solid rgba(104, 158, 225, 0.16);
}

.detail-block span {
  color: var(--muted);
  font-size: 12px;
  font-weight: 800;
}

.detail-block p {
  margin: 7px 0 0;
  color: var(--text);
  line-height: 1.6;
}

@media (max-width: 1100px) {
  .graph-metrics {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
  .span-8,
  .span-4 {
    grid-column: span 12;
  }
}
</style>
