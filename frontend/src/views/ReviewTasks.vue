<template>
  <div class="page">
    <PageHeader title="人工审核" desc="处理低置信度的新岗位、新技能、删除技能和修改技能任务" />
    <div class="panel">
      <el-table :data="rows" stripe>
        <el-table-column prop="task_type" label="任务类型" width="120" />
        <el-table-column prop="title" label="标题" min-width="180" />
        <el-table-column prop="description" label="说明" min-width="260" show-overflow-tooltip />
        <el-table-column label="置信度" width="130">
          <template #default="{ row }">{{ Math.round(row.confidence * 100) }}%</template>
        </el-table-column>
        <el-table-column prop="evidence" label="证据" min-width="220" show-overflow-tooltip />
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === 'pending' ? 'warning' : row.status === 'approved' ? 'success' : 'danger'">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="success" :disabled="row.status !== 'pending'" @click="approve(row.id)">通过</el-button>
            <el-button size="small" type="danger" :disabled="row.status !== 'pending'" @click="reject(row.id)">驳回</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { onMounted, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import { api } from '@/api/http'

const rows = ref<any[]>([])
async function load() {
  rows.value = await api.reviewTasks()
}
async function approve(id: number) {
  await api.approveTask(id)
  ElMessage.success('已通过')
  await load()
}
async function reject(id: number) {
  await api.rejectTask(id)
  ElMessage.success('已驳回')
  await load()
}
onMounted(load)
</script>
