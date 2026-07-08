<template>
  <div class="page jobs-page">
    <PageHeader title="岗位管理" desc="按领域、类型和等级筛选岗位，查看岗位画像、状态、版本和证据来源">
      <div class="job-summary">
        <div>
          <b>{{ rows.length }}</b>
          <span>岗位总数</span>
        </div>
        <div>
          <b>{{ emergingCount }}</b>
          <span>新兴岗位</span>
        </div>
        <div>
          <b>{{ domains.length }}</b>
          <span>覆盖领域</span>
        </div>
      </div>
    </PageHeader>

    <div class="panel">
      <div class="toolbar job-toolbar">
        <el-select v-model="domain" clearable placeholder="所属领域" style="width: 180px">
          <el-option v-for="item in domains" :key="item" :label="item" :value="item" />
        </el-select>
        <el-select v-model="type" clearable placeholder="岗位类型" style="width: 180px">
          <el-option v-for="item in jobTypes" :key="item" :label="item" :value="item" />
        </el-select>
        <el-select v-model="level" clearable placeholder="岗位等级" style="width: 180px">
          <el-option v-for="item in levels" :key="item" :label="item" :value="item" />
        </el-select>
        <el-button @click="resetFilters">重置筛选</el-button>
        <span class="result-count">当前显示 {{ filtered.length }} 条</span>
      </div>

      <el-table :data="filtered" stripe class="job-table" @row-dblclick="openDetail">
        <el-table-column prop="name" label="岗位名称" min-width="190">
          <template #default="{ row }">
            <div class="job-name-cell">
              <span>{{ row.name }}</span>
              <el-tag v-if="row.is_emerging" size="small" type="primary">新岗位</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="domain" label="所属领域" width="120" />
        <el-table-column prop="job_type" label="岗位类型" width="120" />
        <el-table-column prop="level" label="岗位等级" width="110" />
        <el-table-column label="岗位描述" min-width="320">
          <template #default="{ row }">
            <span class="description-ellipsis">{{ row.description }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="version" label="版本号" width="100" />
        <el-table-column label="操作" width="110" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="openDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="detailVisible" class="tech-dialog" width="680px" destroy-on-close align-center>
      <template #header>
        <div class="detail-header">
          <div>
            <div class="detail-kicker">JOB ENTITY PROFILE</div>
            <h3>{{ currentJob?.name }}</h3>
          </div>
          <el-tag :type="currentJob?.is_emerging ? 'primary' : 'info'">
            {{ currentJob?.is_emerging ? '新兴岗位' : '既有岗位' }}
          </el-tag>
        </div>
      </template>

      <div v-if="currentJob" class="detail-body">
        <div class="detail-meta">
          <div><span>所属领域</span><b>{{ currentJob.domain }}</b></div>
          <div><span>岗位类型</span><b>{{ currentJob.job_type }}</b></div>
          <div><span>岗位等级</span><b>{{ currentJob.level }}</b></div>
          <div><span>版本号</span><b>{{ currentJob.version }}</b></div>
        </div>

        <section>
          <h4>岗位描述</h4>
          <p>{{ currentJob.description }}</p>
        </section>

        <section>
          <h4>状态与写入规则</h4>
          <div class="tag-list">
            <el-tag type="success">状态：{{ currentJob.status }}</el-tag>
            <el-tag type="primary">证据可追溯</el-tag>
            <el-tag type="info">低置信度需审核</el-tag>
          </div>
        </section>

        <section>
          <h4>证据来源</h4>
          <div class="evidence-box">{{ currentJob.evidence }}</div>
        </section>
      </div>

      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button type="primary" @click="detailVisible = false">已了解</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import { api } from '@/api/http'

const rows = ref<any[]>([])
const domain = ref('')
const type = ref('')
const level = ref('')
const detailVisible = ref(false)
const currentJob = ref<any>()

const domains = computed(() => Array.from(new Set(rows.value.map((row) => row.domain))))
const jobTypes = computed(() => Array.from(new Set(rows.value.map((row) => row.job_type))))
const levels = computed(() => Array.from(new Set(rows.value.map((row) => row.level))))
const emergingCount = computed(() => rows.value.filter((row) => row.is_emerging).length)
const filtered = computed(() =>
  rows.value.filter(
    (row) =>
      (!domain.value || row.domain === domain.value) &&
      (!type.value || row.job_type === type.value) &&
      (!level.value || row.level === level.value)
  )
)

function resetFilters() {
  domain.value = ''
  type.value = ''
  level.value = ''
}

function openDetail(row: any) {
  currentJob.value = row
  detailVisible.value = true
}

onMounted(async () => {
  rows.value = await api.jobs()
})
</script>

<style scoped>
.job-summary {
  display: grid;
  grid-template-columns: repeat(3, 92px);
  gap: 10px;
}

.job-summary > div {
  border: 1px solid rgba(190, 213, 242, 0.86);
  border-radius: 16px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.65);
  text-align: center;
  box-shadow: 0 10px 26px rgba(37, 99, 235, 0.08);
}

.job-summary b {
  display: block;
  color: #071a3d;
  font-size: 22px;
  font-weight: 950;
}

.job-summary span {
  color: #64748b;
  font-size: 12px;
  font-weight: 800;
}

.job-toolbar {
  margin-bottom: 16px;
}

.result-count {
  margin-left: auto;
  color: #64748b;
  font-size: 13px;
  font-weight: 800;
}

.job-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 900;
  color: #14346c;
}

.description-ellipsis {
  display: -webkit-box;
  overflow: hidden;
  color: #53657e;
  line-height: 1.55;
  text-align: left;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.detail-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.detail-kicker {
  color: var(--cyan);
  font-size: 11px;
  font-weight: 950;
  letter-spacing: 0.16em;
}

.detail-header h3 {
  margin: 8px 0 0;
  color: #071a3d;
  font-size: 23px;
  font-weight: 950;
}

.detail-body {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.detail-meta {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.detail-meta > div {
  border: 1px solid rgba(190, 213, 242, 0.82);
  border-radius: 16px;
  padding: 12px;
  background: rgba(232, 242, 255, 0.52);
}

.detail-meta span {
  display: block;
  color: #64748b;
  font-size: 12px;
  font-weight: 800;
}

.detail-meta b {
  display: block;
  margin-top: 8px;
  color: #0f2f78;
  font-size: 15px;
}

.detail-body section h4 {
  margin: 0 0 9px;
  color: #14346c;
  font-size: 15px;
  font-weight: 950;
}

.detail-body section p {
  margin: 0;
  color: #334155;
  line-height: 1.9;
}

.evidence-box {
  border: 1px solid rgba(6, 182, 212, 0.26);
  border-radius: 16px;
  padding: 13px;
  background: rgba(231, 251, 255, 0.48);
  color: #31506f;
  line-height: 1.8;
}
</style>
