<template>
  <div class="page">
    <PageHeader title="测试评估" desc="一键复现的离线评测：JD 抽取 / 简历抽取 / 人岗匹配的 precision / recall / f1 与错误案例" />

    <div v-if="!metrics.reproducible" class="repro-hint">
      <el-icon><WarningFilled /></el-icon>
      <span>评测样本未就绪，以下指标为回退值。运行 <code>python -m app.evaluation.run_eval</code> 生成可复现结果。</span>
    </div>

    <div class="metric-grid">
      <div class="metric-card"><div class="metric-label">JD 抽取 F1</div><div class="metric-value">{{ metrics.jd_parse_accuracy ?? 0 }}%</div></div>
      <div class="metric-card"><div class="metric-label">简历抽取 F1</div><div class="metric-value">{{ metrics.resume_parse_accuracy ?? 0 }}%</div></div>
      <div class="metric-card"><div class="metric-label">匹配 Top-1 准确率</div><div class="metric-value">{{ metrics.match_accuracy ?? 0 }}%</div></div>
      <div class="metric-card"><div class="metric-label">评测样本数</div><div class="metric-value">{{ metrics.total_samples ?? 0 }}</div></div>
      <div class="metric-card"><div class="metric-label">测试用例数</div><div class="metric-value">{{ metrics.test_case_count || 0 }}</div></div>
      <div class="metric-card"><div class="metric-label">单元测试覆盖率</div><div class="metric-value">{{ metrics.unit_test_coverage ?? 0 }}%</div></div>
    </div>

    <div class="content-grid">
      <div class="panel span-5">
        <div class="panel-heading"><div><span>评测指标对比</span><small>EVAL BAR</small></div></div>
        <EChart :option="option" style="height: 320px" />
      </div>
      <div class="panel span-7">
        <div class="panel-heading"><div><span>分任务评测明细</span><small>TASK METRICS</small></div></div>
        <el-table :data="metrics.tasks || []" stripe>
          <el-table-column prop="task_label" label="任务" />
          <el-table-column prop="samples" label="样本数" width="80" />
          <el-table-column label="Precision" width="100">
            <template #default="{ row }">{{ pct(row.precision) }}</template>
          </el-table-column>
          <el-table-column label="Recall" width="90">
            <template #default="{ row }">{{ pct(row.recall) }}</template>
          </el-table-column>
          <el-table-column label="F1" width="80">
            <template #default="{ row }">{{ pct(row.f1) }}</template>
          </el-table-column>
          <el-table-column label="准确率" width="90">
            <template #default="{ row }">{{ row.accuracy != null ? pct(row.accuracy) : '—' }}</template>
          </el-table-column>
          <el-table-column label="错误案例" width="90">
            <template #default="{ row }">{{ row.error_cases?.length || 0 }}</template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <div class="panel">
      <div class="panel-heading"><div><span>错误案例分析</span><small>ERROR CASES</small></div></div>
      <el-tabs v-model="errorTab">
        <el-tab-pane v-for="t in metrics.tasks || []" :key="t.task" :label="t.task_label" :name="t.task">
          <el-empty v-if="!t.error_cases?.length" description="该任务无错误案例" :image-size="70" />
          <el-table v-else :data="t.error_cases" stripe>
            <el-table-column prop="id" label="样本 ID" width="120" />
            <el-table-column v-if="t.task === 'job_match'" label="金标岗位" width="160">
              <template #default="{ row }">{{ row.gold }}</template>
            </el-table-column>
            <el-table-column v-if="t.task === 'job_match'" label="预测岗位">
              <template #default="{ row }">{{ row.pred }}</template>
            </el-table-column>
            <template v-else>
              <el-table-column label="漏抽(missed)" show-overflow-tooltip>
                <template #default="{ row }">
                  <el-tag v-for="s in row.missed" :key="s" size="small" type="danger" effect="light" style="margin: 2px">{{ s }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="多抽(extra)" show-overflow-tooltip>
                <template #default="{ row }">
                  <el-tag v-for="s in row.extra" :key="s" size="small" type="warning" effect="light" style="margin: 2px">{{ s }}</el-tag>
                </template>
              </el-table-column>
            </template>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </div>

    <div class="panel">
      <div class="panel-heading"><div><span>测试用例</span><small>TEST CASES</small></div></div>
      <el-table :data="metrics.cases || []" stripe>
        <el-table-column prop="case_type" label="类型" width="120" />
        <el-table-column prop="name" label="用例名称" />
        <el-table-column prop="expected" label="期望" show-overflow-tooltip />
        <el-table-column prop="actual" label="结果" />
        <el-table-column label="通过" width="80">
          <template #default="{ row }"><el-tag :type="row.passed ? 'success' : 'warning'">{{ row.passed ? '是' : '复核' }}</el-tag></template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { WarningFilled } from '@element-plus/icons-vue'
import EChart from '@/components/EChart.vue'
import PageHeader from '@/components/PageHeader.vue'
import { api } from '@/api/http'

const metrics = ref<any>({})
const errorTab = ref('')

function pct(v: number | null | undefined) {
  return v == null ? '—' : `${Math.round(v * 100)}%`
}

const option = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 46, right: 22, top: 24, bottom: 30 },
  xAxis: { type: 'category', data: ['JD抽取', '简历抽取', '匹配Top-1', '覆盖率'] },
  yAxis: { type: 'value', max: 100 },
  series: [
    {
      type: 'bar',
      barWidth: 24,
      itemStyle: { borderRadius: [8, 8, 0, 0], color: '#2563eb' },
      data: [metrics.value.jd_parse_accuracy, metrics.value.resume_parse_accuracy, metrics.value.match_accuracy, metrics.value.unit_test_coverage]
    }
  ]
}))

onMounted(async () => {
  metrics.value = await api.evaluation()
  const tasks = metrics.value.tasks || []
  if (tasks.length) errorTab.value = tasks[0].task
})
</script>

<style scoped>
.repro-hint {
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid rgba(245, 158, 11, 0.4);
  border-radius: 14px;
  padding: 12px 16px;
  margin-bottom: 16px;
  background: rgba(245, 158, 11, 0.08);
  color: var(--muted);
  font-size: 13px;
  font-weight: 650;
}

.repro-hint code {
  border-radius: 6px;
  padding: 2px 7px;
  background: rgba(0, 0, 0, 0.06);
  font-size: 12px;
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
</style>
