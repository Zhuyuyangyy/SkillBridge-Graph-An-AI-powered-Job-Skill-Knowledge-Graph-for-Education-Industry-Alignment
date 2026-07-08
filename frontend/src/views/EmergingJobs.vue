<template>
  <div class="page">
    <PageHeader title="新岗位发现" desc="基于技能增长、多源一致性、技能组合新颖度、标题稳定性和场景扩散度计算新岗位指数" />
    <div class="content-grid">
      <div class="panel span-7">
        <el-table :data="rows" highlight-current-row @current-change="current = $event">
          <el-table-column prop="job_name" label="岗位名称" min-width="180" />
          <el-table-column label="新岗位指数" min-width="160">
            <template #default="{ row }"><el-progress :percentage="Math.round(row.emerging_index * 100)" /></template>
          </el-table-column>
          <el-table-column label="关联技能" min-width="220">
            <template #default="{ row }"><el-tag v-for="skill in row.related_skills.slice(0, 3)" :key="skill">{{ skill }}</el-tag></template>
          </el-table-column>
          <el-table-column prop="review_status" label="审核状态" />
        </el-table>
      </div>
      <div class="panel span-5">
        <el-empty v-if="!current" description="选择一个候选岗位查看详情" />
        <template v-else>
          <h3>{{ current.job_name }}</h3>
          <p>{{ current.definition }}</p>
          <el-divider />
          <h4>核心职责</h4>
          <ul><li v-for="item in current.responsibilities" :key="item">{{ item }}</li></ul>
          <h4>必备技能</h4>
          <div class="tag-list"><el-tag v-for="item in current.required_skills" :key="item">{{ item }}</el-tag></div>
          <h4>应用场景</h4>
          <div class="tag-list"><el-tag v-for="item in current.scenarios" :key="item" type="info">{{ item }}</el-tag></div>
          <h4>证据来源</h4>
          <el-alert v-for="item in current.evidence" :key="item.quote" :title="item.quote" :description="item.source" type="info" :closable="false" />
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import { api } from '@/api/http'

const rows = ref<any[]>([])
const current = ref<any>()

onMounted(async () => {
  rows.value = await api.emergingJobs()
  current.value = rows.value[0]
})
</script>
