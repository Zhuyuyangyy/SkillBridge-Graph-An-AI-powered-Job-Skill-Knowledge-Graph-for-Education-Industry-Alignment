<template>
  <div class="page evolution-page">
    <PageHeader title="能力演化" desc="岗位能力随时间的新增、淘汰与迁移趋势分析">
      <el-radio-group v-model="tab" @change="onTabChange">
        <el-radio-button value="timeline">演化时间线</el-radio-button>
        <el-radio-button value="version">版本对比</el-radio-button>
        <el-radio-button value="hotspot">能力热点</el-radio-button>
        <el-radio-button value="compare">领域对比</el-radio-button>
      </el-radio-group>
      <el-button type="primary" :loading="loading" @click="loadAll">刷新数据</el-button>
    </PageHeader>

    <!-- Timeline -->
    <template v-if="tab === 'timeline'">
      <div class="metric-grid evo-metrics">
        <div class="metric-card"><div class="metric-label">更新事件</div><div class="metric-value">{{ timeline.total || 0 }}</div></div>
        <div class="metric-card"><div class="metric-label">新增技能</div><div class="metric-value">{{ sum('added') }}</div></div>
        <div class="metric-card"><div class="metric-label">淘汰技能</div><div class="metric-value">{{ sum('removed') }}</div></div>
        <div class="metric-card"><div class="metric-label">修改技能</div><div class="metric-value">{{ sum('modified') }}</div></div>
      </div>
      <div class="content-grid">
        <section class="panel span-7">
          <div class="panel-heading"><div><span>能力变更趋势</span><small>SKILL DELTA OVER TIME</small></div></div>
          <EChart :option="timelineOption" style="height: 380px" />
        </section>
        <section class="panel span-5">
          <div class="panel-heading"><div><span>更新事件明细</span><small>EVENT LOG</small></div></div>
          <div class="event-list">
            <div v-for="(e, i) in timeline.events" :key="i" class="event-item">
              <div class="event-top">
                <span class="event-job">{{ e.jobName }}</span>
                <el-tag size="small" effect="plain">{{ e.version }}</el-tag>
                <span class="event-date">{{ e.date }}</span>
              </div>
              <p class="event-note">{{ e.note }}</p>
              <div class="event-tags">
                <el-tag v-for="s in e.added" :key="'a' + s" size="small" type="success" effect="light">+{{ s }}</el-tag>
                <el-tag v-for="s in e.removed" :key="'r' + s" size="small" type="danger" effect="light">−{{ s }}</el-tag>
                <el-tooltip v-for="s in e.modified" :key="'m' + s.name" :content="s.change" :disabled="!s.change" placement="top">
                  <el-tag size="small" type="warning" effect="light">~{{ s.name }}</el-tag>
                </el-tooltip>
              </div>
              <div class="event-conf">置信度 {{ (e.confidence * 100).toFixed(0) }}%</div>
            </div>
            <el-empty v-if="!timeline.events?.length" description="暂无更新事件" :image-size="80" />
          </div>
        </section>
      </div>
    </template>

    <!-- Hotspot -->
    <template v-else-if="tab === 'hotspot'">
      <div class="content-grid">
        <section class="panel span-8">
          <div class="panel-heading"><div><span>能力热度排行</span><small>RISING SKILLS</small></div></div>
          <EChart :option="hotspotOption" style="height: 440px" />
        </section>
        <aside class="span-4 hot-side">
          <section class="panel side-block">
            <div class="panel-heading"><div><span>新兴能力</span><small>EMERGING</small></div></div>
            <div class="chip-wrap">
              <span v-for="e in hotspot.emerging" :key="e.name" class="emerging-chip">
                {{ e.name }}<b>×{{ e.growth }}</b>
              </span>
              <el-empty v-if="!hotspot.emerging?.length" description="暂无新兴能力" :image-size="60" />
            </div>
          </section>
          <section class="panel side-block">
            <div class="panel-heading"><div><span>淘汰能力</span><small>DECLINING</small></div></div>
            <div class="decline-list">
              <div v-for="d in hotspot.declining" :key="d.name" class="decline-row">
                <span>{{ d.name }}</span>
                <el-tag size="small" type="danger" effect="light">淘汰 {{ d.removed }}</el-tag>
              </div>
              <el-empty v-if="!hotspot.declining?.length" description="暂无淘汰能力" :image-size="60" />
            </div>
          </section>
        </aside>
      </div>
    </template>

    <!-- Version comparison -->
    <template v-else-if="tab === 'version'">
      <div class="version-hint">
        <el-icon><InfoFilled /></el-icon>
        <span>由岗位能力更新事件重建「上一版 vs 当前版」的能力画像，直观展示每个岗位新增、淘汰、调整了哪些能力及依据。</span>
      </div>
      <div class="content-grid version-cards">
        <section v-for="card in versionCards" :key="card.jobId" class="panel span-6 version-card">
          <div class="version-card__head">
            <div class="version-card__title">
              <span class="vc-job">{{ card.jobName }}</span>
              <el-tag size="small" effect="plain">{{ card.domain }}</el-tag>
            </div>
            <div class="version-badges">
              <span class="ver ver--from">{{ card.fromVersion }}</span>
              <span class="ver-arrow">→</span>
              <span class="ver ver--to">{{ card.toVersion }}</span>
            </div>
          </div>
          <p class="version-note">{{ card.note }}</p>
          <div class="diff-grid">
            <div class="diff-col diff-col--add">
              <div class="diff-label">新增能力 <b>{{ card.added.length }}</b></div>
              <div class="diff-tags">
                <el-tag v-for="s in card.added" :key="'a' + s" size="small" type="success" effect="light">+ {{ s }}</el-tag>
                <span v-if="!card.added.length" class="diff-empty">无</span>
              </div>
            </div>
            <div class="diff-col diff-col--mod">
              <div class="diff-label">调整/替代 <b>{{ card.modified.length }}</b></div>
              <div class="diff-tags">
                <el-tooltip v-for="s in card.modified" :key="'m' + s.name" :content="s.change" :disabled="!s.change" placement="top">
                  <el-tag size="small" type="warning" effect="light">~ {{ s.name }}</el-tag>
                </el-tooltip>
                <span v-if="!card.modified.length" class="diff-empty">无</span>
              </div>
            </div>
            <div class="diff-col diff-col--del">
              <div class="diff-label">淘汰能力 <b>{{ card.removed.length }}</b></div>
              <div class="diff-tags">
                <el-tag v-for="s in card.removed" :key="'r' + s" size="small" type="danger" effect="light">− {{ s }}</el-tag>
                <span v-if="!card.removed.length" class="diff-empty">无</span>
              </div>
            </div>
          </div>
          <div class="version-foot">
            <span class="version-conf">证据置信度 {{ (card.confidence * 100).toFixed(0) }}%</span>
            <span class="version-count">当前能力 {{ card.currentSkills.length }} 项 · 上一版 {{ card.previousSkills.length }} 项</span>
          </div>
        </section>
        <el-empty v-if="!versionCards.length" description="暂无岗位版本更新记录" :image-size="90" />
      </div>
    </template>

    <!-- Compare -->
    <template v-else>
      <section class="panel">
        <div class="panel-heading"><div><span>领域能力结构对比</span><small>DOMAIN × CATEGORY</small></div></div>
        <EChart :option="compareOption" style="height: 420px" />
      </section>
      <div class="content-grid compare-cards">
        <section v-for="row in compare.matrix" :key="row.domain" class="panel span-4 domain-card">
          <div class="domain-title">{{ row.domain }}</div>
          <div class="domain-skills">
            <div v-for="s in row.topSkills" :key="s.name" class="domain-skill">
              <span class="domain-skill__name">{{ s.name }}</span>
              <span class="domain-skill__bar"><i :style="{ width: skillBar(s.weight) }"></i></span>
            </div>
          </div>
        </section>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { InfoFilled } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import EChart from '@/components/EChart.vue'
import { api } from '@/api/http'

const tab = ref('timeline')
const loading = ref(false)
const timeline = ref<any>({ timeline: [], events: [], total: 0 })
const hotspot = ref<any>({ rising: [], declining: [], emerging: [] })
const compare = ref<any>({ categories: [], domains: [], matrix: [] })
const versionCards = ref<any[]>([])

const PALETTE = ['#2563eb', '#06b6d4', '#7c3aed', '#18b981', '#f59e0b', '#ec4899', '#0ea5e9']

function sum(key: string) {
  return (timeline.value.timeline || []).reduce((acc: number, b: any) => acc + (b[key] || 0), 0)
}

const timelineOption = computed(() => {
  const rows = timeline.value.timeline || []
  return {
    textStyle: { color: '#8595ad' },
    tooltip: { trigger: 'axis' },
    legend: { data: ['新增', '淘汰', '修改'], top: 0, textStyle: { color: '#8595ad' } },
    grid: { left: 40, right: 20, top: 40, bottom: 30 },
    xAxis: { type: 'category', data: rows.map((r: any) => r.date), axisLine: { lineStyle: { color: 'rgba(120,150,190,0.4)' } } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(120,150,190,0.14)' } } },
    series: [
      { name: '新增', type: 'bar', stack: 'x', data: rows.map((r: any) => r.added), itemStyle: { color: '#18b981', borderRadius: [4, 4, 0, 0] } },
      { name: '淘汰', type: 'bar', stack: 'x', data: rows.map((r: any) => r.removed), itemStyle: { color: '#f43f5e' } },
      { name: '修改', type: 'bar', stack: 'x', data: rows.map((r: any) => r.modified), itemStyle: { color: '#f59e0b' } },
      {
        name: '事件',
        type: 'line',
        smooth: true,
        data: rows.map((r: any) => r.events),
        lineStyle: { color: '#2563eb', width: 3 },
        itemStyle: { color: '#2563eb' },
        areaStyle: { color: 'rgba(37,99,235,0.08)' }
      }
    ]
  }
})

const hotspotOption = computed(() => {
  const rows = [...(hotspot.value.rising || [])].reverse()
  return {
    textStyle: { color: '#8595ad' },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 90, right: 30, top: 20, bottom: 30 },
    xAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(120,150,190,0.14)' } } },
    yAxis: {
      type: 'category',
      data: rows.map((r: any) => r.name),
      axisLine: { lineStyle: { color: 'rgba(120,150,190,0.4)' } }
    },
    series: [
      {
        type: 'bar',
        data: rows.map((r: any, i: number) => ({
          value: r.heat,
          itemStyle: { color: PALETTE[i % PALETTE.length], borderRadius: [0, 6, 6, 0] }
        })),
        barWidth: '58%',
        label: { show: true, position: 'right', formatter: '{c}', color: '#8595ad', fontWeight: 700 }
      }
    ]
  }
})

const compareOption = computed(() => {
  const cats = compare.value.categories || []
  const domains = compare.value.domains || []
  const matrix = compare.value.matrix || []
  return {
    textStyle: { color: '#8595ad' },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: cats, top: 0, type: 'scroll', textStyle: { color: '#8595ad' } },
    grid: { left: 40, right: 20, top: 40, bottom: 60 },
    xAxis: { type: 'category', data: domains, axisLabel: { interval: 0, rotate: 24 }, axisLine: { lineStyle: { color: 'rgba(120,150,190,0.4)' } } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(120,150,190,0.14)' } } },
    series: cats.map((cat: string, i: number) => ({
      name: cat,
      type: 'bar',
      stack: 'total',
      data: matrix.map((row: any) => row.categories[cat] || 0),
      itemStyle: { color: PALETTE[i % PALETTE.length] }
    }))
  }
})

const maxWeight = computed(() => {
  let m = 1
  for (const row of compare.value.matrix || []) {
    for (const s of row.topSkills || []) m = Math.max(m, s.weight)
  }
  return m
})

function skillBar(weight: number) {
  return `${Math.round((weight / maxWeight.value) * 100)}%`
}

async function loadAll() {
  loading.value = true
  try {
    const [t, h, c, v] = await Promise.all([
      api.evolutionTimeline(),
      api.evolutionHotspot(),
      api.evolutionCompare(),
      api.evolutionVersionCompare()
    ])
    timeline.value = t
    hotspot.value = h
    compare.value = c
    versionCards.value = Array.isArray(v?.cards) ? v.cards : []
  } finally {
    loading.value = false
  }
}

function onTabChange() {
  /* charts are reactive via computed options */
}

onMounted(loadAll)
</script>

<style scoped>
.evolution-page {
  min-width: 0;
}

.evo-metrics {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.panel-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
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

/* Version comparison */
.version-hint {
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid rgba(6, 182, 212, 0.28);
  border-radius: 14px;
  padding: 12px 16px;
  background: rgba(6, 182, 212, 0.07);
  color: var(--muted);
  font-size: 13px;
  font-weight: 650;
}

.version-hint .el-icon {
  flex: 0 0 auto;
  color: var(--cyan);
  font-size: 18px;
}

.version-cards {
  margin-top: 4px;
}

.version-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 18px 20px;
}

.version-card__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.version-card__title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.vc-job {
  color: var(--text);
  font-size: 16px;
  font-weight: 900;
}

.version-badges {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 0 0 auto;
}

.ver {
  border-radius: 8px;
  padding: 3px 10px;
  font-size: 12px;
  font-weight: 850;
}

.ver--from {
  border: 1px solid rgba(148, 163, 184, 0.5);
  background: rgba(148, 163, 184, 0.14);
  color: var(--muted);
}

.ver--to {
  border: 1px solid rgba(37, 99, 235, 0.4);
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.16), rgba(6, 182, 212, 0.14));
  color: var(--primary);
}

.ver-arrow {
  color: var(--muted);
  font-weight: 800;
}

.version-note {
  margin: 0;
  color: var(--muted);
  font-size: 13px;
  line-height: 1.6;
}

.diff-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.diff-col {
  border-radius: 14px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.42);
  border: 1px solid rgba(190, 213, 242, 0.5);
}

.diff-col--add {
  border-color: rgba(24, 185, 129, 0.32);
  background: rgba(24, 185, 129, 0.06);
}

.diff-col--mod {
  border-color: rgba(245, 158, 11, 0.32);
  background: rgba(245, 158, 11, 0.06);
}

.diff-col--del {
  border-color: rgba(244, 63, 94, 0.3);
  background: rgba(244, 63, 94, 0.05);
}

.diff-label {
  margin-bottom: 10px;
  color: var(--text);
  font-size: 12px;
  font-weight: 850;
}

.diff-label b {
  color: var(--primary);
}

.diff-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.diff-empty {
  color: var(--muted);
  font-size: 12px;
}

.version-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  border-top: 1px solid rgba(104, 158, 225, 0.16);
  padding-top: 10px;
}

.version-conf {
  color: var(--cyan);
  font-size: 12px;
  font-weight: 800;
}

.version-count {
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
}

.event-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 380px;
  overflow-y: auto;
  padding-right: 6px;
}

.event-item {
  border: 1px solid rgba(190, 213, 242, 0.5);
  border-radius: 14px;
  padding: 12px 14px;
  background: rgba(255, 255, 255, 0.5);
}

.event-top {
  display: flex;
  align-items: center;
  gap: 8px;
}

.event-job {
  color: var(--text);
  font-weight: 850;
}

.event-date {
  margin-left: auto;
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
}

.event-note {
  margin: 8px 0;
  color: var(--muted);
  font-size: 13px;
  line-height: 1.55;
}

.event-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.event-conf {
  margin-top: 8px;
  color: var(--cyan);
  font-size: 12px;
  font-weight: 800;
}

.hot-side {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.side-block {
  padding: 18px;
}

.chip-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.emerging-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid rgba(124, 58, 237, 0.3);
  border-radius: 999px;
  padding: 6px 12px;
  background: linear-gradient(135deg, rgba(124, 58, 237, 0.12), rgba(37, 99, 235, 0.08));
  color: #7c3aed;
  font-size: 13px;
  font-weight: 800;
}

.emerging-chip b {
  color: var(--primary);
  font-size: 11px;
}

.decline-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.decline-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(104, 158, 225, 0.16);
  padding: 8px 2px;
  color: var(--text);
  font-weight: 700;
}

.compare-cards {
  margin-top: 18px;
}

.domain-card {
  padding: 16px 18px;
}

.domain-title {
  margin-bottom: 12px;
  color: var(--text);
  font-size: 15px;
  font-weight: 900;
}

.domain-skills {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.domain-skill {
  display: grid;
  grid-template-columns: 100px 1fr;
  align-items: center;
  gap: 10px;
}

.domain-skill__name {
  overflow: hidden;
  color: var(--muted);
  font-size: 12px;
  font-weight: 750;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.domain-skill__bar {
  height: 8px;
  border-radius: 99px;
  background: rgba(190, 213, 242, 0.42);
  overflow: hidden;
}

.domain-skill__bar i {
  display: block;
  height: 100%;
  border-radius: 99px;
  background: linear-gradient(90deg, var(--primary), var(--cyan));
}

@media (max-width: 1100px) {
  .evo-metrics {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .span-7,
  .span-5,
  .span-8,
  .span-6,
  .span-4 {
    grid-column: span 12;
  }
}
</style>
