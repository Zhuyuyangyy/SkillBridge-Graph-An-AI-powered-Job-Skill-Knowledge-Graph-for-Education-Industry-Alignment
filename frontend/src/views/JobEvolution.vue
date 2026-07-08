<template>
  <div class="page">
    <PageHeader title="岗位能力更新" desc="选择岗位后查看新增、删除、修改技能和版本记录">
      <el-select v-model="jobId" placeholder="选择岗位" style="width: 260px" @change="loadEvolution">
        <el-option v-for="job in jobs" :key="job.id" :label="job.name" :value="job.id" />
      </el-select>
    </PageHeader>
    <div class="content-grid">
      <div class="panel span-6">
        <h3>技能变化</h3>
        <el-table :data="changeRows">
          <el-table-column prop="type" label="类型" width="120" />
          <el-table-column prop="skill" label="技能/说明" />
        </el-table>
      </div>
      <div class="panel span-6">
        <h3>版本记录</h3>
        <el-timeline>
          <el-timeline-item v-for="item in evolution?.timeline || []" :key="item.time" :timestamp="String(item.time)">
            {{ item.content }}
          </el-timeline-item>
        </el-timeline>
        <el-alert v-if="evolution" :title="evolution.update_note" :description="`证据：${evolution.evidence}`" type="info" :closable="false" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import { api } from '@/api/http'

const jobs = ref<any[]>([])
const jobId = ref<number>()
const evolution = ref<any>()
const changeRows = computed(() => {
  if (!evolution.value) return []
  return [
    ...evolution.value.added_skills.map((skill: string) => ({ type: '新增技能', skill })),
    ...evolution.value.removed_skills.map((skill: string) => ({ type: '删除技能', skill })),
    ...evolution.value.modified_skills.map((skill: any) => ({ type: '修改技能', skill: typeof skill === 'string' ? skill : `${skill.skill}：${skill.change}` }))
  ]
})

async function loadEvolution() {
  if (!jobId.value) return
  evolution.value = await api.jobEvolution(jobId.value)
}

onMounted(async () => {
  jobs.value = await api.jobs()
  jobId.value = jobs.value[0]?.id
  await loadEvolution()
})
</script>
