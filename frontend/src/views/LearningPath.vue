<template>
  <div class="page learning-page">
    <PageHeader title="学习路径" desc="基于最近一次人岗匹配差距，生成基础、核心、项目、部署和提升阶段的成长路线">
      <div class="toolbar">
        <el-button @click="router.push('/match-analysis')">返回匹配分析</el-button>
        <el-button type="primary" :loading="loading" @click="load">刷新路径</el-button>
      </div>
    </PageHeader>

    <section class="learning-hero panel">
      <div class="learning-summary">
        <span>最近一次匹配结论</span>
        <h3>{{ report?.target_job || '目标岗位待选择' }}</h3>
        <p>{{ aiAnalysis?.note || '系统会根据匹配报告中的缺失技能、风险点和岗位要求生成阶段化学习建议。' }}</p>
      </div>
      <div class="score-card">
        <span>综合匹配度</span>
        <strong>{{ report?.total_score ?? '-' }}%</strong>
        <em>{{ scoreLabel }}</em>
      </div>
      <div class="missing-card">
        <span>优先补齐</span>
        <div class="tag-list">
          <el-tag v-for="item in missingSkills" :key="item" type="danger" effect="light">{{ item }}</el-tag>
          <el-tag v-if="!missingSkills.length" type="success" effect="light">暂无明显短板</el-tag>
        </div>
      </div>
    </section>

    <div class="content-grid">
      <section class="panel span-8">
        <div class="section-head">
          <div>
            <span>阶段路线</span>
            <h3>从补基础到项目证明</h3>
          </div>
          <small>每个阶段都对应具体产出，方便更新简历和准备面试表达</small>
        </div>
        <div class="path-timeline">
          <article v-for="(item, index) in path" :key="item.stage" class="path-card">
            <div class="stage-index">{{ String(index + 1).padStart(2, '0') }}</div>
            <div>
              <h3>{{ item.stage }}</h3>
              <p>{{ item.content }}</p>
              <div class="path-detail">
                <span><b>建议项目：</b>{{ item.project }}</span>
                <span><b>预计周期：</b>{{ item.duration }}</span>
                <span><b>前置技能：</b>{{ item.prerequisites?.length ? item.prerequisites.join('、') : '无' }}</span>
              </div>
            </div>
          </article>
        </div>
      </section>

      <aside class="panel span-4 learning-side">
        <div class="section-head compact">
          <div>
            <span>执行清单</span>
            <h3>本周建议</h3>
          </div>
        </div>
        <div class="todo-list">
          <div v-for="item in weeklyTodos" :key="item" class="todo-item">{{ item }}</div>
        </div>

        <div class="side-block">
          <h3>生成说明</h3>
          <p>{{ aiAnalysis?.summary || '当前路径会结合匹配报告、岗位技能和缺失项生成，并可进一步细化到课程、项目和练习题。' }}</p>
          <div class="tag-list">
            <el-tag v-for="item in aiAnalysis?.stages || []" :key="item" type="primary" effect="light">{{ item }}</el-tag>
          </div>
        </div>

        <div class="side-actions">
          <el-button type="primary" @click="router.push('/resume-parser')">更新简历证据</el-button>
          <el-button @click="router.push('/digital-interviewer')">面试练习</el-button>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import PageHeader from '@/components/PageHeader.vue'
import { api } from '@/api/http'

const router = useRouter()
const path = ref<any[]>([])
const aiAnalysis = ref<any>()
const report = ref<any>()
const loading = ref(false)

const missingSkills = computed<string[]>(() => report.value?.missing_skills || [])
const scoreLabel = computed(() => {
  const score = Number(report.value?.total_score || 0)
  if (score >= 85) return '高度匹配'
  if (score >= 70) return '建议复核'
  if (score >= 55) return '可培养'
  return '需系统补强'
})
const weeklyTodos = computed(() => {
  const first = missingSkills.value.slice(0, 2)
  if (!first.length) return ['整理一个项目复盘：背景、个人负责内容、结果', '完善岗位相关证书或课程记录', '准备 3 分钟项目介绍']
  return [
    `先把 ${first[0]} 的基础用法过一遍，并做一份笔记`,
    first[1] ? `围绕 ${first[1]} 做一个小任务，写清楚你怎么完成的` : '做一个能讲清楚过程的小项目',
    '把新的项目经历同步到个人画像和简历文本',
    '使用数字人面试官进行一次追问练习'
  ]
})

async function load() {
  loading.value = true
  try {
    const cached = localStorage.getItem('last_match_report')
    report.value = cached ? JSON.parse(cached) : undefined
    const response = await api.learningPath(1)
    const rows = Array.isArray(response) ? response : response.items
    path.value = enrichPath(rows || [])
    aiAnalysis.value = Array.isArray(response) ? undefined : response.ai_analysis
  } finally {
    loading.value = false
  }
}

function enrichPath(rows: any[]) {
  if (!missingSkills.value.length) return rows
  return rows.map((item, index) => ({
    ...item,
    content: index < missingSkills.value.length ? `${missingSkills.value[index]}：${item.content}` : item.content
  }))
}

onMounted(load)
</script>

<style scoped>
.learning-hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 220px 360px;
  gap: 16px;
  align-items: stretch;
}

.learning-summary,
.score-card,
.missing-card {
  border: 1px solid rgba(190, 213, 242, 0.74);
  border-radius: 18px;
  padding: 18px;
  background: rgba(255, 255, 255, 0.58);
  transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
}

.learning-summary:hover,
.missing-card:hover,
.path-card:hover,
.todo-item:hover {
  border-color: rgba(6, 182, 212, 0.42);
  box-shadow: 0 18px 42px rgba(37, 99, 235, 0.12);
  transform: translateY(-2px);
}

.learning-summary span,
.missing-card span,
.score-card span,
.section-head span {
  color: var(--cyan);
  font-size: 11px;
  font-weight: 950;
  letter-spacing: 0.14em;
}

.learning-summary h3 {
  margin: 10px 0 8px;
  color: #071a3d;
  font-size: 24px;
}

.learning-summary p,
.side-block p {
  margin: 0;
  color: #53657e;
  font-size: 14px;
  font-weight: 700;
  line-height: 1.8;
}

.score-card {
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: center;
  color: #fff;
  background:
    radial-gradient(circle at 18% 14%, rgba(255, 255, 255, 0.34), transparent 30%),
    linear-gradient(135deg, #2563eb, #06b6d4);
}

.score-card::after {
  position: absolute;
  right: -34px;
  bottom: -48px;
  width: 118px;
  height: 118px;
  content: "";
  border: 1px dashed rgba(255, 255, 255, 0.42);
  border-radius: 50%;
  animation: learningRing 13s linear infinite;
}

.score-card span {
  color: rgba(255, 255, 255, 0.78);
}

.score-card strong {
  margin-top: 10px;
  font-size: 42px;
  line-height: 1;
}

.score-card em {
  margin-top: 10px;
  font-style: normal;
  font-weight: 900;
}

.missing-card .tag-list {
  margin-top: 14px;
}

.section-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.section-head h3 {
  margin: 7px 0 0;
  color: #071a3d;
}

.section-head small {
  color: #64748b;
  font-size: 13px;
  font-weight: 700;
}

.section-head.compact {
  margin-bottom: 12px;
}

.path-timeline {
  display: grid;
  gap: 14px;
}

.path-card {
  display: grid;
  grid-template-columns: 54px minmax(0, 1fr);
  gap: 14px;
  border: 1px solid rgba(190, 213, 242, 0.74);
  border-radius: 18px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.58);
  transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
}

.stage-index {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  border-radius: 16px;
  color: #fff;
  background: linear-gradient(135deg, #2563eb, #06b6d4);
  font-weight: 950;
}

.path-card h3 {
  margin: 0 0 8px;
  color: #0f2148;
}

.path-card p {
  margin: 0;
  color: #334155;
  font-weight: 760;
  line-height: 1.7;
}

.path-detail {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-top: 12px;
}

.path-detail span {
  border-radius: 14px;
  padding: 10px;
  color: #53657e;
  background: rgba(232, 242, 255, 0.74);
  font-size: 13px;
  line-height: 1.55;
}

.learning-side {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.todo-list {
  display: grid;
  gap: 10px;
}

.todo-item {
  border: 1px solid rgba(190, 213, 242, 0.74);
  border-radius: 15px;
  padding: 12px;
  color: #243856;
  background: rgba(255, 255, 255, 0.62);
  font-size: 14px;
  font-weight: 780;
  line-height: 1.6;
  transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
}

@keyframes learningRing {
  to {
    transform: rotate(360deg);
  }
}

.side-block {
  border-top: 1px solid rgba(190, 213, 242, 0.72);
  padding-top: 14px;
}

.side-block h3 {
  margin: 0 0 10px;
}

.side-block .tag-list {
  margin-top: 12px;
}

.side-actions {
  display: grid;
  gap: 10px;
  margin-top: auto;
}

@media (max-width: 1100px) {
  .learning-hero,
  .path-detail {
    grid-template-columns: 1fr;
  }
}
</style>
