<template>
  <div class="page match-page">
    <PageHeader title="匹配分析" desc="选择简历与目标岗位，查看匹配结论、能力差距、风险提醒和下一步行动">
      <div class="toolbar analysis-toolbar">
        <el-select v-model="resumeId" placeholder="选择简历" filterable style="width: 210px">
          <el-option v-for="item in resumeOptions" :key="item.id" :label="item.name" :value="item.id" />
        </el-select>
        <el-select v-model="jobId" placeholder="目标岗位" filterable style="width: 260px">
          <el-option v-for="item in jobs" :key="item.id" :label="item.name" :value="item.id" />
        </el-select>
        <el-button type="primary" :loading="loading" @click="submit">开始分析</el-button>
      </div>
    </PageHeader>

    <section class="panel match-hero">
      <div class="hero-card candidate-card">
        <div class="avatar">{{ selectedResume?.name?.slice(0, 1) || '候' }}</div>
        <div class="hero-copy">
          <span>候选人画像</span>
          <h3>{{ selectedResume?.name || '未选择简历' }}</h3>
          <p>{{ selectedResumeSummary }}</p>
          <div class="mini-tags">
            <el-tag v-if="selectedResume?.intention" type="primary" effect="light">{{ selectedResume.intention }}</el-tag>
            <el-tag v-if="selectedResume?.certificates?.length" type="success" effect="light">
              {{ selectedResume.certificates.length }} 项证书
            </el-tag>
          </div>
        </div>
      </div>

      <div class="hero-card job-card">
        <div class="job-icon">JOB</div>
        <div class="hero-copy">
          <span>目标岗位</span>
          <h3>{{ selectedJob?.name || '未选择岗位' }}</h3>
          <p>{{ selectedJobProfile }}</p>
          <div class="mini-tags">
            <el-tag v-if="selectedJob?.domain" effect="light">{{ selectedJob.domain }}</el-tag>
            <el-tag v-if="selectedJob?.level" type="warning" effect="light">{{ selectedJob.level }}</el-tag>
          </div>
        </div>
      </div>

      <div class="score-badge" :class="scoreLevel.className">
        <span>综合匹配度</span>
        <strong>{{ report?.total_score ?? '-' }}%</strong>
        <em>{{ scoreLevel.label }}</em>
      </div>
    </section>

    <section class="analysis-layout">
      <div class="panel score-panel">
        <div class="section-head">
          <div>
            <span>评分拆解</span>
            <h3>六项维度匹配</h3>
          </div>
          <el-tag :type="scoreLevel.tagType" effect="light">{{ scoreLevel.label }}</el-tag>
        </div>

        <div class="dimension-list">
          <div v-for="item in dimensionRows" :key="item.name" class="dimension-row">
            <div class="dimension-meta">
              <b>{{ item.name }}</b>
              <span>{{ dimensionAdvice(item.score) }}</span>
            </div>
            <div class="dimension-value">
              <el-progress :percentage="item.score" :stroke-width="10" :show-text="false" />
              <strong>{{ item.score }}%</strong>
            </div>
          </div>
        </div>

        <div class="formula-card">
          <b>计算规则</b>
          <p>必备技能 40% + 加分技能 15% + 项目经验 20% + 工具平台 10% + 行业场景 10% + 证书成果 5%。</p>
        </div>
      </div>

      <div class="panel radar-panel">
        <div class="section-head">
          <div>
            <span>能力雷达</span>
            <h3>覆盖强弱对比</h3>
          </div>
          <small>越接近外圈，说明该维度证据越充分</small>
        </div>
        <div class="radar-box">
          <EChart :option="radarOption" />
        </div>
      </div>

      <div class="panel gap-panel">
        <div class="section-head">
          <div>
            <span>差距清单</span>
            <h3>缺失技能与补强动作</h3>
          </div>
          <small>优先补齐岗位必备项</small>
        </div>
        <div v-if="missingSkills.length" class="missing-grid">
          <article v-for="(item, index) in missingSkills" :key="item" class="missing-card">
            <span>{{ index + 1 }}</span>
            <b>{{ item }}</b>
            <p>{{ gapDescription(item) }}</p>
          </article>
        </div>
        <el-empty v-else description="当前必备技能已基本覆盖" :image-size="90" />
      </div>

      <div class="panel evidence-panel">
        <div class="section-head">
          <div>
            <span>改进建议</span>
            <h3>可执行改进项</h3>
          </div>
          <small>可以直接用于修改简历和安排学习计划</small>
        </div>
        <div class="action-list">
          <div v-for="(item, index) in suggestions" :key="item" class="action-item">
            <em>{{ index + 1 }}</em>
            <span>{{ item }}</span>
          </div>
        </div>
      </div>
    </section>

    <section class="panel ai-panel">
      <div class="ai-summary">
        <div>
          <span>系统分析</span>
          <h3>综合结论</h3>
          <p>{{ aiSummary }}</p>
        </div>
        <el-tag effect="light" type="primary">分析接口已就绪</el-tag>
      </div>

      <div class="ai-columns">
        <div class="ai-box">
          <h4>下一步提升</h4>
          <ul>
            <li v-for="item in aiSuggestions" :key="item">{{ item }}</li>
          </ul>
        </div>
        <div class="ai-box warning">
          <h4>风险点</h4>
          <ul>
            <li v-for="item in riskPoints" :key="item">{{ item }}</li>
          </ul>
        </div>
      </div>
      <div class="ai-actions">
        <el-button type="primary" @click="router.push('/learning-path')">生成学习路径</el-button>
        <el-button @click="router.push('/digital-interviewer')">进入面试练习</el-button>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import EChart from '@/components/EChart.vue'
import PageHeader from '@/components/PageHeader.vue'
import { api } from '@/api/http'
import { useAuthStore } from '@/stores/auth'

type DimensionRow = {
  name: string
  score: number
}

const jobs = ref<any[]>([])
const resumes = ref<any[]>([])
const profile = ref<any>()
const jobId = ref<number>()
const resumeId = ref<number>()
const report = ref<any>()
const loading = ref(false)
const router = useRouter()
const auth = useAuthStore()
let alive = true

const fallbackDimensions: DimensionRow[] = [
  { name: '必备技能', score: 0 },
  { name: '加分技能', score: 0 },
  { name: '项目经验', score: 0 },
  { name: '工具平台', score: 0 },
  { name: '行业场景', score: 0 },
  { name: '证书成果', score: 0 }
]

const dimensionRows = computed<DimensionRow[]>(() => {
  const rows = report.value?.dimension_rows
  return Array.isArray(rows) && rows.length ? rows : fallbackDimensions
})

const resumeOptions = computed(() => {
  const rows = resumes.value.map((item) => ({ ...item, name: item.name || `简历 ${item.id}` }))
  if (auth.role !== 'candidate' || !profile.value) return rows
  return [{ id: -1, name: '我的个人画像' }, ...rows]
})
const selectedJob = computed(() => jobs.value.find((item) => item.id === jobId.value))
const selectedResume = computed(() => {
  if (resumeId.value === -1 && profile.value) {
    return {
      id: -1,
      name: profile.value.real_name || auth.user?.display_name || '我的画像',
      education: profile.value.education,
      major: profile.value.major,
      school: profile.value.school,
      certificates: profile.value.certificates || [],
      intention: profile.value.target_role,
      skills: profile.value.skills || [],
      projects: profile.value.projects || [],
      internships: profile.value.internships || []
    }
  }
  return resumes.value.find((item) => item.id === resumeId.value)
})

const selectedResumeSummary = computed(() => {
  const resume = selectedResume.value
  if (!resume) return '请选择一份简历后开始分析'
  return `${resume.education || '学历未知'} · ${resume.major || '专业未知'} · ${resume.school || '学校未知'}`
})

const selectedJobProfile = computed(() => {
  const job = selectedJob.value
  if (!job) return '请选择目标岗位'
  return `${job.domain || '领域未标注'} · ${job.level || '等级未标注'} · ${job.job_type || '岗位类型未标注'}`
})

const missingSkills = computed<string[]>(() => report.value?.missing_skills || [])
const suggestions = computed<string[]>(() => report.value?.suggestions || ['请选择简历和岗位后生成改进建议'])
const aiSummary = computed(() => {
  return report.value?.ai_analysis?.summary || '系统会根据简历内容和岗位要求给出整体判断，并整理出下一步最该处理的事项。'
})
const aiSuggestions = computed<string[]>(() => report.value?.ai_analysis?.suggestions || suggestions.value)
const riskPoints = computed<string[]>(() => report.value?.ai_analysis?.risk_points || ['关键经历还不够具体', '项目结果最好写得更清楚'])

const scoreLevel = computed(() => {
  const score = Number(report.value?.total_score || 0)
  if (score >= 85) return { label: '高度匹配', className: 'excellent', tagType: 'success' as const }
  if (score >= 70) return { label: '推荐复核', className: 'good', tagType: 'primary' as const }
  if (score >= 55) return { label: '可培养', className: 'medium', tagType: 'warning' as const }
  return { label: '差距较大', className: 'low', tagType: 'danger' as const }
})

const radarOption = computed(() => ({
  tooltip: {
    trigger: 'item',
    backgroundColor: 'rgba(15, 23, 42, .9)',
    borderWidth: 0,
    textStyle: { color: '#fff' }
  },
  radar: {
    radius: '66%',
    center: ['50%', '53%'],
    splitNumber: 4,
    axisName: { color: '#516178', fontWeight: 700 },
    splitLine: { lineStyle: { color: ['rgba(148,163,184,.22)'] } },
    splitArea: { areaStyle: { color: ['rgba(37,99,235,.035)', 'rgba(6,182,212,.06)'] } },
    axisLine: { lineStyle: { color: 'rgba(148,163,184,.32)' } },
    indicator: dimensionRows.value.map((item) => ({ name: item.name, max: 100 }))
  },
  series: [
    {
      name: '匹配维度',
      type: 'radar',
      areaStyle: { color: 'rgba(37,99,235,.2)' },
      lineStyle: { color: '#2563eb', width: 2 },
      itemStyle: { color: '#06b6d4' },
      symbolSize: 6,
      data: [{ value: dimensionRows.value.map((item) => item.score || 0) }]
    }
  ]
}))

async function submit() {
  loading.value = true
  try {
    const payload =
      resumeId.value === -1 && selectedResume.value
        ? {
            resume: {
              skills: selectedResume.value.skills || [],
              certificates: selectedResume.value.certificates || [],
              projects: selectedResume.value.projects || [],
              internships: selectedResume.value.internships || []
            },
            target_job_id: jobId.value
          }
        : { resume_id: resumeId.value, target_job_id: jobId.value }
    const result = await api.matchAnalysis(payload)
    if (alive) {
      report.value = result
      localStorage.setItem('last_match_report', JSON.stringify(result))
    }
  } finally {
    loading.value = false
  }
}

function dimensionAdvice(score: number) {
  if (score >= 85) return '这一项比较稳，可以放在简历前面'
  if (score >= 70) return '基本够用，最好再写清楚做过什么'
  if (score >= 50) return '有基础，但还缺少能说明问题的经历'
  return '差距比较明显，建议先从入门任务做起'
}

function gapDescription(skill: string) {
  if (/RAG|Prompt|LangChain|向量|模型|大模型/.test(skill)) return '做一个小型知识库或问答项目，把数据来源、检索流程、回答效果和你负责的部分写清楚。'
  if (/Docker|Kubernetes|Linux|Git|部署|运维/.test(skill)) return '准备一次完整部署经历：环境怎么搭、服务怎么启动、出问题时怎么排查。'
  if (/SQL|数据|Hive|Spark|Flink|治理|血缘/.test(skill)) return '整理一段数据处理经历，说明数据从哪来、怎么清洗、最后支持了什么业务判断。'
  return `给 ${skill} 准备一段真实经历：学了什么、做了什么、结果怎么样。`
}

onMounted(async () => {
  const requests: Promise<any>[] = [api.jobs(), api.resumes()]
  if (auth.role === 'candidate') requests.push(api.myProfile())
  const [jobRows, resumeRows, myProfile] = await Promise.all(requests)
  jobs.value = jobRows
  resumes.value = resumeRows
  profile.value = myProfile
  jobId.value = jobs.value[0]?.id
  resumeId.value = auth.role === 'candidate' && profile.value ? -1 : resumes.value[0]?.id
  await submit()
})

onBeforeUnmount(() => {
  alive = false
})
</script>

<style scoped>
.match-page {
  gap: 20px;
}

.analysis-toolbar {
  justify-content: flex-end;
}

.match-hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) 260px;
  gap: 16px;
  align-items: stretch;
}

.hero-card {
  display: flex;
  gap: 16px;
  align-items: center;
  min-height: 142px;
  border: 1px solid rgba(190, 213, 242, 0.78);
  border-radius: 18px;
  padding: 18px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.82), rgba(234, 247, 255, 0.54)),
    rgba(255, 255, 255, 0.58);
  transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
}

.hero-card:hover,
.dimension-row:hover,
.missing-card:hover,
.action-item:hover {
  border-color: rgba(6, 182, 212, 0.42);
  box-shadow: 0 18px 42px rgba(37, 99, 235, 0.12);
  transform: translateY(-2px);
}

.avatar,
.job-icon {
  display: grid;
  flex: 0 0 auto;
  place-items: center;
  width: 70px;
  height: 70px;
  border-radius: 24px;
  color: #fff;
  font-size: 24px;
  font-weight: 950;
  background:
    radial-gradient(circle at 32% 22%, rgba(255, 255, 255, 0.86), transparent 25%),
    linear-gradient(135deg, #2563eb, #06b6d4);
  box-shadow: 0 18px 34px rgba(37, 99, 235, 0.24);
}

.job-icon {
  font-size: 16px;
  letter-spacing: 0.08em;
}

.hero-copy {
  min-width: 0;
}

.hero-copy span,
.section-head span,
.ai-summary span {
  color: #06a6cc;
  font-size: 12px;
  font-weight: 950;
  letter-spacing: 0.12em;
}

.hero-copy h3 {
  margin: 7px 0 8px;
  color: #071a3d;
  font-size: 22px;
  line-height: 1.25;
}

.hero-copy p {
  overflow: hidden;
  margin: 0;
  color: #53657e;
  font-size: 14px;
  font-weight: 700;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mini-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.score-badge {
  display: flex;
  position: relative;
  flex-direction: column;
  justify-content: center;
  min-height: 142px;
  overflow: hidden;
  border: 1px solid rgba(6, 182, 212, 0.38);
  border-radius: 20px;
  padding: 22px;
  color: #fff;
  background:
    radial-gradient(circle at 22% 18%, rgba(255, 255, 255, 0.36), transparent 28%),
    linear-gradient(135deg, #0f2f78, #2563eb 50%, #06b6d4);
  box-shadow: 0 20px 44px rgba(37, 99, 235, 0.25);
}

.score-badge::after {
  position: absolute;
  right: -30px;
  bottom: -52px;
  width: 146px;
  height: 146px;
  content: "";
  border: 1px dashed rgba(255, 255, 255, 0.42);
  border-radius: 50%;
  animation: scoreRing 14s linear infinite;
}

.score-badge span {
  font-size: 13px;
  font-weight: 850;
  opacity: 0.84;
}

.score-badge strong {
  margin-top: 8px;
  font-size: 48px;
  line-height: 1;
}

.score-badge em {
  width: fit-content;
  margin-top: 12px;
  border-radius: 999px;
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.18);
  font-style: normal;
  font-weight: 900;
}

.score-badge.medium {
  background:
    radial-gradient(circle at 22% 18%, rgba(255, 255, 255, 0.36), transparent 28%),
    linear-gradient(135deg, #1d4ed8, #0ea5e9 54%, #22c55e);
}

.score-badge.low {
  background:
    radial-gradient(circle at 22% 18%, rgba(255, 255, 255, 0.32), transparent 28%),
    linear-gradient(135deg, #334155, #2563eb 55%, #f59e0b);
}

.analysis-layout {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: 18px;
}

.score-panel {
  grid-column: span 5;
  min-height: 450px;
}

.radar-panel {
  grid-column: span 7;
  min-height: 450px;
}

.gap-panel,
.evidence-panel {
  grid-column: span 6;
  min-height: 310px;
}

.section-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.section-head h3,
.ai-summary h3 {
  margin: 6px 0 0;
  color: #071a3d;
  font-size: 22px;
  line-height: 1.2;
}

.section-head small {
  color: #6b7a90;
  font-size: 13px;
  font-weight: 700;
}

.dimension-list {
  display: grid;
  gap: 14px;
}

.dimension-row {
  border: 1px solid rgba(190, 213, 242, 0.72);
  border-radius: 16px;
  padding: 14px;
  background: rgba(255, 255, 255, 0.58);
  transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
}

.dimension-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 10px;
}

.dimension-meta b {
  color: #0f2148;
  font-size: 15px;
}

.dimension-meta span {
  color: #687991;
  font-size: 12px;
  font-weight: 700;
}

.dimension-value {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 54px;
  gap: 12px;
  align-items: center;
}

.dimension-value strong {
  color: #12306c;
  text-align: right;
}

.formula-card {
  margin-top: 18px;
  border: 1px solid rgba(6, 182, 212, 0.22);
  border-radius: 18px;
  padding: 16px;
  background:
    radial-gradient(circle at 8% 12%, rgba(6, 182, 212, 0.13), transparent 30%),
    rgba(232, 242, 255, 0.58);
}

.formula-card b {
  color: #0f2f78;
  font-size: 15px;
}

.formula-card p {
  margin: 8px 0 0;
  color: #53657e;
  font-size: 13px;
  font-weight: 700;
  line-height: 1.7;
}

.radar-box {
  height: 370px;
}

.radar-box :deep(.chart) {
  height: 100%;
}

.missing-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.missing-card {
  position: relative;
  overflow: hidden;
  min-height: 120px;
  border: 1px solid rgba(248, 113, 113, 0.22);
  border-radius: 18px;
  padding: 16px 16px 14px;
  background:
    linear-gradient(145deg, rgba(255, 255, 255, 0.84), rgba(255, 241, 242, 0.52)),
    rgba(255, 255, 255, 0.52);
  transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
}

.missing-card span {
  display: grid;
  place-items: center;
  width: 30px;
  height: 30px;
  border-radius: 10px;
  color: #dc2626;
  background: rgba(254, 226, 226, 0.9);
  font-weight: 950;
}

.missing-card b {
  display: block;
  margin-top: 12px;
  color: #0f2148;
  font-size: 16px;
}

.missing-card p {
  margin: 8px 0 0;
  color: #64748b;
  font-size: 13px;
  font-weight: 650;
  line-height: 1.6;
}

.action-list {
  display: grid;
  gap: 12px;
}

.action-item {
  display: grid;
  grid-template-columns: 36px minmax(0, 1fr);
  align-items: center;
  gap: 12px;
  border: 1px solid rgba(190, 213, 242, 0.72);
  border-radius: 16px;
  padding: 13px 14px;
  background: rgba(255, 255, 255, 0.62);
  transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
}

.action-item em {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border-radius: 12px;
  color: #fff;
  background: linear-gradient(135deg, #2563eb, #06b6d4);
  font-style: normal;
  font-weight: 950;
}

.action-item span {
  color: #253858;
  font-size: 14px;
  font-weight: 750;
  line-height: 1.7;
}

.ai-panel {
  display: grid;
  grid-template-columns: 0.95fr 1.35fr;
  gap: 18px;
  align-items: stretch;
}

.ai-summary {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 220px;
  border: 1px solid rgba(6, 182, 212, 0.24);
  border-radius: 18px;
  padding: 18px;
  background:
    radial-gradient(circle at 12% 8%, rgba(6, 182, 212, 0.14), transparent 30%),
    rgba(255, 255, 255, 0.58);
}

.ai-summary p {
  margin: 12px 0 22px;
  color: #3f5068;
  font-size: 14px;
  font-weight: 700;
  line-height: 1.9;
}

.ai-columns {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.ai-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  grid-column: 2;
}

.ai-box {
  border: 1px solid rgba(190, 213, 242, 0.72);
  border-radius: 18px;
  padding: 18px;
  background: rgba(255, 255, 255, 0.62);
}

.ai-box.warning {
  border-color: rgba(245, 158, 11, 0.28);
  background:
    radial-gradient(circle at 10% 0%, rgba(245, 158, 11, 0.12), transparent 28%),
    rgba(255, 255, 255, 0.62);
}

.ai-box h4 {
  margin: 0 0 12px;
  color: #0f2148;
  font-size: 17px;
}

.ai-box ul {
  display: grid;
  gap: 10px;
  margin: 0;
  padding-left: 18px;
  color: #334155;
  font-size: 14px;
  font-weight: 720;
  line-height: 1.75;
}

@keyframes scoreRing {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 1100px) {
  .match-hero,
  .ai-panel {
    grid-template-columns: 1fr;
  }

  .ai-actions {
    grid-column: auto;
  }

  .score-panel,
  .radar-panel,
  .gap-panel,
  .evidence-panel {
    grid-column: span 12;
  }
}
</style>
