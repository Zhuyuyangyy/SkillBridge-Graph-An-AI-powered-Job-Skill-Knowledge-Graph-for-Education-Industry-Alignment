<template>
  <div class="page eval-page">
    <PageHeader title="测试评估" desc="展示 JD 解析、简历解析、匹配分析、测试用例数量和可复现评测结果" />

    <div class="metric-grid">
      <div class="metric-card"><div class="metric-label">JD 解析准确率</div><div class="metric-value">{{ metrics.jd_parse_accuracy }}%</div></div>
      <div class="metric-card"><div class="metric-label">简历解析准确率</div><div class="metric-value">{{ metrics.resume_parse_accuracy }}%</div></div>
      <div class="metric-card"><div class="metric-label">匹配准确率</div><div class="metric-value">{{ metrics.match_accuracy }}%</div></div>
      <div class="metric-card"><div class="metric-label">测试用例数量</div><div class="metric-value">{{ metrics.test_case_count || 0 }}</div></div>
      <div class="metric-card"><div class="metric-label">单元测试覆盖率</div><div class="metric-value">{{ metrics.unit_test_coverage }}%</div></div>
    </div>

    <!-- Reproducible evaluation report -->
    <section class="panel report-panel">
      <div class="report-head">
        <div>
          <span class="report-title">可复现评测报告</span>
          <small>REPRODUCIBLE EVALUATION · 现场运行离线评测，产出指标与错误案例</small>
        </div>
        <div class="report-cmd">
          <code>$ {{ report.command || 'python -m app.evaluation.run_eval' }}</code>
          <el-button size="small" type="primary" :loading="reportLoading" @click="loadReport">重新运行</el-button>
        </div>
      </div>

      <div v-loading="reportLoading" class="report-grid">
        <article v-for="task in report.results" :key="task.task" class="report-card" :style="{ '--c': taskColor(task.task) }">
          <div class="report-card__head">
            <span class="report-card__name">{{ task.task_label }}</span>
            <el-tag size="small" effect="plain">{{ task.samples }} 样本</el-tag>
          </div>
          <div class="report-card__score">
            <span class="score-num">{{ mainScore(task) }}<i>%</i></span>
            <span class="score-lbl">{{ task.accuracy != null ? 'Top-1 准确率' : 'F1 分数' }}</span>
          </div>
          <div v-if="task.precision != null" class="prf">
            <div class="prf-row" v-for="m in prfRows(task)" :key="m.label">
              <span class="prf-label">{{ m.label }}</span>
              <span class="prf-bar"><i :style="{ width: m.value * 100 + '%' }"></i></span>
              <span class="prf-val">{{ (m.value * 100).toFixed(1) }}%</span>
            </div>
          </div>
          <div class="report-card__foot">
            <span v-if="task.error_cases.length" class="err-count">{{ task.error_cases.length }} 个错误案例</span>
            <span v-else class="err-count ok">全部命中</span>
          </div>
        </article>
      </div>

      <div v-if="allErrors.length" class="error-block">
        <div class="error-block__head">错误案例分析<small>ERROR CASES</small></div>
        <div class="error-list">
          <div v-for="(e, i) in allErrors" :key="i" class="error-item">
            <el-tag size="small" :type="e.kind === 'match' ? 'danger' : 'warning'" effect="light">{{ e.taskLabel }}</el-tag>
            <span class="error-id">{{ e.id }}</span>
            <template v-if="e.kind === 'match'">
              <span class="err-detail">应为 <b class="gold">{{ e.gold }}</b>，预测 <b class="pred">{{ e.pred }}</b></span>
            </template>
            <template v-else>
              <span v-if="e.missed?.length" class="err-detail">漏检 <b class="miss">{{ e.missed.join('、') }}</b></span>
              <span v-if="e.extra?.length" class="err-detail">多检 <b class="extra">{{ e.extra.join('、') }}</b></span>
            </template>
          </div>
        </div>
      </div>
    </section>

    <div class="content-grid">
      <div class="panel span-5">
        <div class="panel-title-row"><span>准确率概览</span></div>
        <EChart :option="option" />
      </div>
      <div class="panel span-7">
        <div class="panel-title-row"><span>测试用例明细</span></div>
        <el-table :data="metrics.cases || []" stripe>
          <el-table-column prop="case_type" label="类型" />
          <el-table-column prop="name" label="用例名称" />
          <el-table-column prop="expected" label="期望" show-overflow-tooltip />
          <el-table-column prop="actual" label="结果" />
          <el-table-column label="通过">
            <template #default="{ row }"><el-tag :type="row.passed ? 'success' : 'warning'">{{ row.passed ? '是' : '复核' }}</el-tag></template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import EChart from '@/components/EChart.vue'
import PageHeader from '@/components/PageHeader.vue'
import { api } from '@/api/http'

const metrics = ref<any>({})
const report = ref<any>({ command: '', results: [] })
const reportLoading = ref(false)

const TASK_COLORS: Record<string, string> = {
  jd_extraction: '#2563eb',
  resume_extraction: '#06b6d4',
  job_match: '#f59e0b'
}

function taskColor(task: string) {
  return TASK_COLORS[task] || '#7c3aed'
}

function mainScore(task: any) {
  const v = task.accuracy != null ? task.accuracy : task.f1
  return v != null ? (v * 100).toFixed(1) : '—'
}

function prfRows(task: any) {
  return [
    { label: 'P', value: task.precision ?? 0 },
    { label: 'R', value: task.recall ?? 0 },
    { label: 'F1', value: task.f1 ?? 0 }
  ]
}

const allErrors = computed(() => {
  const out: any[] = []
  for (const task of report.value.results || []) {
    const kind = task.task === 'job_match' ? 'match' : 'extract'
    for (const e of task.error_cases || []) {
      out.push({ ...e, kind, taskLabel: task.task_label })
    }
  }
  return out
})

const option = computed(() => ({
  textStyle: { color: '#8595ad' },
  tooltip: {},
  grid: { left: 40, right: 20, top: 20, bottom: 30 },
  xAxis: { type: 'category', data: ['JD解析', '简历解析', '匹配分析', '覆盖率'], axisLine: { lineStyle: { color: 'rgba(120,150,190,0.4)' } } },
  yAxis: { type: 'value', max: 100, splitLine: { lineStyle: { color: 'rgba(120,150,190,0.14)' } } },
  series: [
    {
      type: 'bar',
      barWidth: '46%',
      itemStyle: { color: '#1768d1', borderRadius: [6, 6, 0, 0] },
      data: [metrics.value.jd_parse_accuracy, metrics.value.resume_parse_accuracy, metrics.value.match_accuracy, metrics.value.unit_test_coverage]
    }
  ]
}))

async function loadReport() {
  reportLoading.value = true
  try {
    report.value = await api.evaluationReport()
  } finally {
    reportLoading.value = false
  }
}

onMounted(async () => {
  metrics.value = await api.evaluation()
  await loadReport()
})
</script>

<style scoped>
.eval-page {
  min-width: 0;
}

.panel-title-row {
  margin-bottom: 14px;
  color: var(--text);
  font-size: 16px;
  font-weight: 900;
}

.report-panel {
  padding: 22px;
}

.report-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 14px;
  margin-bottom: 18px;
}

.report-title {
  color: var(--text);
  font-size: 18px;
  font-weight: 900;
}

.report-head small {
  display: block;
  margin-top: 6px;
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
}

.report-cmd {
  display: flex;
  align-items: center;
  gap: 10px;
}

.report-cmd code {
  border: 1px solid rgba(37, 99, 235, 0.24);
  border-radius: 10px;
  padding: 8px 12px;
  background: rgba(12, 28, 58, 0.06);
  color: var(--primary);
  font-size: 13px;
  font-weight: 700;
  font-family: 'SF Mono', 'Consolas', monospace;
}

.report-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.report-card {
  position: relative;
  overflow: hidden;
  border: 1px solid color-mix(in srgb, var(--c) 30%, transparent);
  border-radius: 18px;
  padding: 18px;
  background: linear-gradient(160deg, color-mix(in srgb, var(--c) 8%, rgba(255, 255, 255, 0.5)), rgba(255, 255, 255, 0.35));
}

.report-card::before {
  content: '';
  position: absolute;
  top: -24px;
  right: -24px;
  width: 74px;
  height: 74px;
  border-radius: 50%;
  background: var(--c);
  filter: blur(40px);
  opacity: 0.3;
}

.report-card__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.report-card__name {
  color: var(--text);
  font-size: 15px;
  font-weight: 900;
}

.report-card__score {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 14px;
}

.score-num {
  color: var(--c);
  font-size: 34px;
  font-weight: 950;
  line-height: 1;
}

.score-num i {
  font-size: 15px;
  font-style: normal;
}

.score-lbl {
  color: var(--muted);
  font-size: 12px;
  font-weight: 750;
}

.prf {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.prf-row {
  display: grid;
  grid-template-columns: 24px 1fr 48px;
  align-items: center;
  gap: 8px;
}

.prf-label {
  color: var(--muted);
  font-size: 12px;
  font-weight: 850;
}

.prf-bar {
  height: 7px;
  border-radius: 99px;
  background: rgba(190, 213, 242, 0.4);
  overflow: hidden;
}

.prf-bar i {
  display: block;
  height: 100%;
  border-radius: 99px;
  background: var(--c);
}

.prf-val {
  color: var(--text);
  font-size: 12px;
  font-weight: 800;
  text-align: right;
}

.report-card__foot {
  margin-top: 14px;
}

.err-count {
  color: var(--orange);
  font-size: 12px;
  font-weight: 800;
}

.err-count.ok {
  color: var(--green);
}

.error-block {
  margin-top: 20px;
  border-top: 1px solid rgba(104, 158, 225, 0.16);
  padding-top: 16px;
}

.error-block__head {
  margin-bottom: 12px;
  color: var(--text);
  font-size: 15px;
  font-weight: 900;
}

.error-block__head small {
  margin-left: 8px;
  color: var(--cyan);
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.14em;
}

.error-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.error-item {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  border: 1px solid rgba(190, 213, 242, 0.5);
  border-radius: 12px;
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.4);
}

.error-id {
  color: var(--muted);
  font-size: 12px;
  font-weight: 800;
  font-family: 'SF Mono', 'Consolas', monospace;
}

.err-detail {
  color: var(--text);
  font-size: 13px;
}

.err-detail b {
  font-weight: 850;
}

.err-detail .gold,
.err-detail .miss {
  color: var(--primary);
}

.err-detail .pred,
.err-detail .extra {
  color: var(--orange);
}

@media (max-width: 1100px) {
  .report-grid {
    grid-template-columns: 1fr;
  }
  .span-5,
  .span-7 {
    grid-column: span 12;
  }
}
</style>
