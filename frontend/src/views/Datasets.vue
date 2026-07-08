<template>
  <div class="page">
    <PageHeader title="数据源管理" desc="管理多源 JD 数据，观察质量评分、重复率、噪声率和处理状态">
      <div class="toolbar">
        <el-button type="primary" :icon="Plus">新增数据源</el-button>
        <el-button :icon="Upload">上传</el-button>
      </div>
    </PageHeader>
    <div class="panel">
      <el-table :data="rows" stripe>
        <el-table-column prop="source_name" label="数据来源" min-width="150" />
        <el-table-column prop="data_type" label="数据类型" />
        <el-table-column prop="domain" label="所属领域" />
        <el-table-column prop="uploaded_at" label="上传时间" min-width="170" />
        <el-table-column prop="data_count" label="数据量" />
        <el-table-column label="重复率">
          <template #default="{ row }">{{ pct(row.duplicate_rate) }}</template>
        </el-table-column>
        <el-table-column label="噪声率">
          <template #default="{ row }">{{ pct(row.noise_rate) }}</template>
        </el-table-column>
        <el-table-column label="质量评分" min-width="130">
          <template #default="{ row }"><el-progress :percentage="row.quality_score" :stroke-width="8" /></template>
        </el-table-column>
        <el-table-column label="处理状态">
          <template #default="{ row }"><el-tag :type="row.status === 'processed' ? 'success' : 'warning'">{{ row.status }}</el-tag></template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Plus, Upload } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { api } from '@/api/http'

const rows = ref<any[]>([])
const pct = (value: number) => `${Math.round(value * 100)}%`

onMounted(async () => {
  rows.value = await api.datasets()
})
</script>
