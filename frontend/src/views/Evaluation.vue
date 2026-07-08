<template>
  <div class="page">
    <PageHeader title="测试评估" desc="展示 JD 解析、简历解析、匹配分析、测试用例数量和单元测试评估结果" />
    <div class="metric-grid">
      <div class="metric-card"><div class="metric-label">JD 解析准确率</div><div class="metric-value">{{ metrics.jd_parse_accuracy }}%</div></div>
      <div class="metric-card"><div class="metric-label">简历解析准确率</div><div class="metric-value">{{ metrics.resume_parse_accuracy }}%</div></div>
      <div class="metric-card"><div class="metric-label">匹配准确率</div><div class="metric-value">{{ metrics.match_accuracy }}%</div></div>
      <div class="metric-card"><div class="metric-label">测试用例数量</div><div class="metric-value">{{ metrics.test_case_count || 0 }}</div></div>
      <div class="metric-card"><div class="metric-label">单元测试覆盖率</div><div class="metric-value">{{ metrics.unit_test_coverage }}%</div></div>
    </div>
    <div class="content-grid">
      <div class="panel span-5">
        <EChart :option="option" />
      </div>
      <div class="panel span-7">
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
const option = computed(() => ({
  tooltip: {},
  xAxis: { type: 'category', data: ['JD解析', '简历解析', '匹配分析', '覆盖率'] },
  yAxis: { type: 'value', max: 100 },
  series: [{ type: 'bar', itemStyle: { color: '#1768d1' }, data: [metrics.value.jd_parse_accuracy, metrics.value.resume_parse_accuracy, metrics.value.match_accuracy, metrics.value.unit_test_coverage] }]
}))

onMounted(async () => {
  metrics.value = await api.evaluation()
})
</script>
