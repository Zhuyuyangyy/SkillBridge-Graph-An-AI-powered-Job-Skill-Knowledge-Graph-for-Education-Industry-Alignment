<template>
  <div class="page skill-graph-page">
    <PageHeader title="能力图谱" desc="查看岗位、技能、工具、证书、课程与行业场景之间的关联">
      <div class="toolbar">
        <el-input
          v-model="keyword"
          clearable
          placeholder="搜索岗位、技能或证书"
          style="width: 230px"
          @input="renderGraph"
        />
        <el-select v-model="nodeType" clearable placeholder="全部节点" style="width: 144px" @change="renderGraph">
          <el-option v-for="item in types" :key="item" :label="typeLabels[item] || item" :value="item" />
        </el-select>
        <el-button type="primary" :loading="loading" @click="loadGraph">刷新图谱</el-button>
      </div>
    </PageHeader>

    <section class="graph-overview" aria-label="图谱统计">
      <div class="graph-overview__item"><strong>{{ raw.nodes.length }}</strong><span>关联节点</span></div>
      <div class="graph-overview__item"><strong>{{ raw.edges.length }}</strong><span>关系连线</span></div>
      <div class="graph-overview__item graph-overview__hint">
        <span>拖拽节点可整理布局，滚轮缩放，点击节点查看关联说明。</span>
      </div>
    </section>

    <div class="content-grid">
      <section class="panel span-8 graph-panel">
        <div v-loading="loading" class="graph-stage">
          <div ref="containerRef" class="graph-box"></div>
          <div v-if="!loading && graphError" class="graph-message">
            <el-empty description="图谱暂时无法加载">
              <el-button type="primary" @click="loadGraph">重新加载</el-button>
            </el-empty>
          </div>
          <div v-else-if="!loading && !visibleData.nodes.length" class="graph-message">
            <el-empty description="没有符合条件的节点" />
          </div>
        </div>
      </section>

      <aside class="panel span-4 graph-detail-panel">
        <div class="detail-heading">
          <span>节点详情</span>
          <small>NODE DETAIL</small>
        </div>
        <el-empty v-if="!selected" description="点击图谱节点查看详情" />
        <template v-else>
          <div class="selected-node" :style="{ '--node-color': nodeColor(selected.type) }">
            <span class="selected-node__dot"></span>
            <div>
              <h3>{{ selected.label }}</h3>
              <el-tag effect="plain">{{ typeLabels[selected.type] || selected.type }}</el-tag>
            </div>
          </div>
          <div class="detail-block">
            <span>证据来源</span>
            <p>{{ selected.evidence || '该节点已进入图谱，暂未补充来源说明。' }}</p>
          </div>
          <div v-if="selected.category" class="detail-block">
            <span>分类</span>
            <p>{{ selected.category }}</p>
          </div>
          <div class="detail-block">
            <span>关联关系</span>
            <p>{{ relationshipCount(selected.id) }} 条</p>
          </div>
        </template>
      </aside>
    </div>

    <section class="graph-legend">
      <span v-for="item in types" :key="item" class="graph-legend__item">
        <i :style="{ background: nodeColor(item) }"></i>{{ typeLabels[item] || item }}
      </span>
    </section>
  </div>
</template>

<script setup lang="ts">
import * as echarts from 'echarts'
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import { api } from '@/api/http'

type GraphNode = {
  id: string
  label: string
  type: string
  category?: string
  evidence?: string
}

type GraphEdge = {
  source: string
  target: string
  label?: string
  evidence?: string
}

const containerRef = ref<HTMLDivElement>()
const raw = ref<{ nodes: GraphNode[]; edges: GraphEdge[] }>({ nodes: [], edges: [] })
const keyword = ref('')
const nodeType = ref('')
const selected = ref<GraphNode>()
const loading = ref(false)
const graphError = ref(false)
let chart: echarts.ECharts | undefined
let resizeObserver: ResizeObserver | undefined

const typeLabels: Record<string, string> = {
  Job: '岗位',
  Skill: '技能',
  Tool: '工具平台',
  Certificate: '证书',
  Responsibility: '职责',
  IndustryScenario: '行业场景',
  Course: '课程',
  Level: '能力等级'
}

const types = computed(() => Array.from(new Set(raw.value.nodes.map((node) => node.type))))
const visibleData = computed(() => filteredData())

function nodeColor(type: string) {
  const colors: Record<string, string> = {
    Job: '#1768d1',
    Skill: '#1e91f2',
    Tool: '#14b8a6',
    Certificate: '#8b5cf6',
    Responsibility: '#f59e0b',
    IndustryScenario: '#0ea5e9',
    Course: '#10b981',
    Level: '#ec4899'
  }
  return colors[type] || '#7ca0c8'
}

function filteredData() {
  const normalizedKeyword = keyword.value.trim().toLowerCase()
  const nodes = raw.value.nodes
    .filter((node) => {
      const isKeywordMatch = !normalizedKeyword || node.label.toLowerCase().includes(normalizedKeyword)
      return isKeywordMatch && (!nodeType.value || node.type === nodeType.value)
    })
    .slice(0, 85)
  const ids = new Set(nodes.map((node) => node.id))
  const edges = raw.value.edges.filter((edge) => ids.has(edge.source) && ids.has(edge.target)).slice(0, 180)
  return { nodes, edges }
}

async function renderGraph() {
  await nextTick()
  const container = containerRef.value
  if (!container) return

  const data = filteredData()
  if (!data.nodes.length) {
    chart?.clear()
    return
  }

  chart ??= echarts.init(container)
  chart.setOption({
    animationDuration: 700,
    animationDurationUpdate: 420,
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(10, 40, 91, 0.9)',
      borderColor: 'rgba(133, 210, 255, 0.45)',
      textStyle: { color: '#eff9ff' },
      formatter: (params: any) => {
        if (params.dataType === 'edge') return `${params.data.label || '关联关系'}`
        return `<b>${params.data.name}</b><br/>${typeLabels[params.data.raw.type] || params.data.raw.type}`
      }
    },
    series: [{
      type: 'graph',
      layout: 'force',
      roam: true,
      draggable: true,
      focusNodeAdjacency: true,
      data: data.nodes.map((node) => ({
        id: node.id,
        name: node.label,
        raw: node,
        symbolSize: node.type === 'Job' ? 54 : node.type === 'Skill' ? 38 : 32,
        itemStyle: {
          color: nodeColor(node.type),
          borderColor: '#ffffff',
          borderWidth: 2.4,
          shadowBlur: 16,
          shadowColor: `${nodeColor(node.type)}66`
        }
      })),
      links: data.edges.map((edge) => ({ source: edge.source, target: edge.target, label: edge.label, raw: edge })),
      label: {
        show: true,
        position: 'bottom',
        distance: 7,
        color: '#173665',
        fontSize: 11,
        fontWeight: 600,
        formatter: (params: any) => params.data.name.length > 10 ? `${params.data.name.slice(0, 10)}...` : params.data.name
      },
      edgeLabel: { show: false },
      lineStyle: { color: '#93b7df', width: 1.3, opacity: 0.58, curveness: 0.08 },
      emphasis: {
        focus: 'adjacency',
        scale: true,
        lineStyle: { width: 2.4, opacity: 0.92 },
        label: { fontSize: 13, fontWeight: 800, color: '#102d5a' }
      },
      force: { repulsion: 290, edgeLength: [76, 152], gravity: 0.08, friction: 0.55, layoutAnimation: true }
    }]
  }, true)

  chart.off('click')
  chart.on('click', (params: any) => {
    if (params.dataType === 'node') selected.value = params.data.raw
  })
}

function relationshipCount(id: string) {
  return raw.value.edges.filter((edge) => edge.source === id || edge.target === id).length
}

async function loadGraph() {
  loading.value = true
  graphError.value = false
  try {
    const response = await api.skillGraph()
    raw.value = {
      nodes: Array.isArray(response?.nodes) ? response.nodes : [],
      edges: Array.isArray(response?.edges) ? response.edges : []
    }
    if (selected.value && !raw.value.nodes.some((node) => node.id === selected.value?.id)) selected.value = undefined
    await renderGraph()
  } catch {
    graphError.value = true
    chart?.clear()
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadGraph()
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
.skill-graph-page {
  min-width: 0;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
}

.graph-overview {
  display: flex;
  align-items: stretch;
  gap: 10px;
  margin: 0 0 16px;
}

.graph-overview__item {
  min-width: 115px;
  padding: 10px 16px;
  border: 1px solid rgba(87, 164, 255, 0.24);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.56);
  box-shadow: 0 10px 26px rgba(31, 104, 188, 0.07);
}

.graph-overview strong {
  display: block;
  color: #1768d1;
  font-size: 20px;
  line-height: 1.1;
}

.graph-overview span {
  color: #6881a8;
  font-size: 12px;
  font-weight: 700;
}

.graph-overview__hint {
  display: grid;
  flex: 1;
  place-items: center start;
}

.graph-stage {
  position: relative;
  min-height: 560px;
}

.graph-box {
  height: 560px;
  border: 1px solid rgba(37, 99, 235, 0.28);
  border-radius: 16px;
  overflow: hidden;
  background:
    linear-gradient(rgba(37, 99, 235, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(37, 99, 235, 0.05) 1px, transparent 1px),
    radial-gradient(circle at 18% 10%, rgba(6, 182, 212, 0.16), transparent 28%),
    linear-gradient(135deg, rgba(248, 251, 255, 0.92), rgba(231, 244, 255, 0.82));
  background-size: 34px 34px, 34px 34px, auto, auto;
  box-shadow: inset 0 0 42px rgba(6, 182, 212, 0.08);
}

.graph-message {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  background: rgba(248, 252, 255, 0.64);
}

.graph-detail-panel {
  min-height: 560px;
}

.detail-heading {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 10px;
  color: #15386d;
  font-size: 17px;
  font-weight: 900;
}

.detail-heading small {
  color: #00a8d7;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.13em;
}

.selected-node {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border: 1px solid rgba(78, 154, 255, 0.25);
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(230, 244, 255, 0.86), rgba(255, 255, 255, 0.72));
}

.selected-node h3 {
  margin: 0 0 7px;
  color: #102f60;
}

.selected-node__dot {
  width: 18px;
  height: 18px;
  flex: 0 0 auto;
  border: 5px solid rgba(255, 255, 255, 0.92);
  border-radius: 50%;
  background: var(--node-color);
  box-shadow: 0 0 0 5px color-mix(in srgb, var(--node-color) 17%, transparent), 0 0 18px var(--node-color);
}

.detail-block {
  padding: 15px 1px;
  border-bottom: 1px solid rgba(104, 158, 225, 0.18);
}

.detail-block span {
  color: #6580ab;
  font-size: 12px;
  font-weight: 800;
}

.detail-block p {
  margin: 7px 0 0;
  color: #23436e;
  line-height: 1.65;
}

.graph-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 16px;
  margin-top: 16px;
  padding: 0 4px;
}

.graph-legend__item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #58749e;
  font-size: 12px;
  font-weight: 750;
}

.graph-legend__item i {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  box-shadow: 0 0 10px currentColor;
}

@media (max-width: 980px) {
  .graph-overview { flex-wrap: wrap; }
  .graph-overview__hint { min-width: 250px; }
  .span-8, .span-4 { grid-column: span 12; }
  .graph-detail-panel { min-height: 260px; }
}

@media (max-width: 640px) {
  .toolbar { justify-content: stretch; }
  .toolbar :deep(.el-input), .toolbar :deep(.el-select), .toolbar :deep(.el-button) { width: 100% !important; }
  .graph-stage, .graph-box { min-height: 430px; height: 430px; }
}
</style>
