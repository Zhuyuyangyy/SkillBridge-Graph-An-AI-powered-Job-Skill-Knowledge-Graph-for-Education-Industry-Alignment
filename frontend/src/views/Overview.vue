<template>
  <div class="page overview-page">
    <section class="overview-hero">
      <div class="hero-copy">
        <div class="hero-kicker">岗位画像与匹配</div>
        <h1>数融智联岗位能力图谱</h1>
        <p>
          {{ isCandidate ? '维护个人资料，解析简历，查看目标岗位的匹配情况、能力差距和学习建议。' : '汇总岗位样本，维护岗位与能力关系，跟进候选人、岗位变化和待审核内容。' }}
        </p>
        <div class="hero-actions">
          <el-button v-for="action in heroActions" :key="action.path" :type="action.primary ? 'primary' : 'default'" @click="$router.push(action.path)">
            {{ action.label }}
          </el-button>
        </div>
      </div>

      <div class="hero-network">
        <div class="orbit orbit-outer"></div>
        <div class="orbit orbit-inner"></div>
        <div class="network-core">
          <span>{{ summary.skill_count ?? 0 }}</span>
          <b>技能实体</b>
        </div>
        <i class="node node-a"></i>
        <i class="node node-b"></i>
        <i class="node node-c"></i>
        <i class="node node-d"></i>
        <i class="link link-a"></i>
        <i class="link link-b"></i>
        <i class="link link-c"></i>
      </div>
    </section>

    <div class="overview-metrics">
      <article v-for="item in primaryMetrics" :key="item.label" class="overview-metric">
        <div class="metric-top">
          <span>{{ item.label }}</span>
          <em>{{ item.badge }}</em>
        </div>
        <strong>{{ item.value }}</strong>
        <small>{{ item.desc }}</small>
      </article>
    </div>

    <section class="panel span-12 workflow-panel">
      <div class="panel-heading">
        <div>
          <h3>常用流程</h3>
          <p>{{ isCandidate ? '按求职准备顺序进入常用模块。' : '按岗位数据维护顺序进入常用模块。' }}</p>
        </div>
        <el-tag type="success">可点击进入</el-tag>
      </div>
      <div class="workflow-lane">
        <button v-for="(step, index) in workflowSteps" :key="step.title" class="workflow-step" @click="$router.push(step.path)">
          <span>{{ String(index + 1).padStart(2, '0') }}</span>
          <b>{{ step.title }}</b>
          <small>{{ step.desc }}</small>
        </button>
      </div>
    </section>

    <div class="content-grid">
      <div class="panel span-8 trend-panel">
        <div class="panel-heading">
          <div>
            <h3>数据变化趋势</h3>
            <p>近 14 天入库、技能和更新记录</p>
          </div>
          <el-tag type="primary">最近更新</el-tag>
        </div>
        <EChart :option="trendOption" />
      </div>

      <div class="panel span-4 quality-panel">
        <div class="panel-heading compact">
          <div>
            <h3>质量指标</h3>
            <p>解析、匹配和测试结果</p>
          </div>
        </div>
        <div class="quality-list">
          <div v-for="item in qualityMetrics" :key="item.label" class="quality-item">
            <div>
              <span>{{ item.label }}</span>
              <b>{{ item.value }}%</b>
            </div>
            <el-progress :percentage="item.value" :stroke-width="10" />
          </div>
        </div>
      </div>

      <div class="panel span-4">
        <div class="panel-heading compact">
          <div>
            <h3>岗位领域</h3>
            <p>岗位库按领域统计</p>
          </div>
        </div>
        <EChart :option="barOption" />
      </div>

      <div class="panel span-4">
        <div class="panel-heading compact">
          <div>
            <h3>图谱状态</h3>
            <p>关系、岗位和变更记录</p>
          </div>
        </div>
        <div class="graph-status">
          <div>
            <span>图谱关系</span>
            <b>{{ summary.graph_relation_count ?? '-' }}</b>
          </div>
          <div>
            <span>新岗位</span>
            <b>{{ summary.emerging_job_count ?? '-' }}</b>
          </div>
          <div>
            <span>更新事件</span>
            <b>{{ summary.evolution_event_count ?? '-' }}</b>
          </div>
        </div>
      </div>

      <div class="panel span-4">
        <div class="panel-heading compact">
          <div>
            <h3>{{ isCandidate ? '下一步' : '待处理' }}</h3>
            <p>{{ isCandidate ? '补齐资料后再查看匹配结果' : '优先处理会影响图谱的数据' }}</p>
          </div>
        </div>
        <div class="task-list">
          <button v-for="task in roleTasks" :key="task.title" @click="$router.push(task.path)">
            <span>{{ task.title }}</span>
            <small>{{ task.desc }}</small>
          </button>
        </div>
      </div>

      <div class="panel span-12 guard-panel">
        <div>
          <h3>待复核内容</h3>
          <p>{{ isCandidate ? '图谱内容来自岗位库和审核记录，可用于查看目标岗位的能力要求。' : '来源不足或置信度较低的变更先进入审核，确认后再进入岗位库和图谱。' }}</p>
        </div>
        <el-button type="primary" @click="$router.push(isCandidate ? '/skill-graph' : '/review-tasks')">
          {{ isCandidate ? '查看能力图谱' : '查看审核任务' }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import EChart from '@/components/EChart.vue'
import { api } from '@/api/http'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const summary = ref<any>({})
const isCandidate = computed(() => auth.role === 'candidate')

const heroActions = computed(() =>
  isCandidate.value
    ? [
        { label: '完善个人画像', path: '/personal-center', primary: true },
        { label: '开始匹配分析', path: '/match-analysis', primary: false },
        { label: '查看学习路径', path: '/learning-path', primary: false }
      ]
    : [
        { label: '管理数据源', path: '/datasets', primary: true },
        { label: '解析 JD', path: '/jd-parser', primary: false },
        { label: '查看能力图谱', path: '/skill-graph', primary: false }
      ]
)

const primaryMetrics = computed(() => [
  { label: 'JD 样本', value: summary.value.jd_count ?? '-', badge: 'DATA', desc: '已入库岗位文本' },
  { label: '岗位', value: summary.value.job_count ?? '-', badge: 'JOB', desc: '岗位库当前规模' },
  { label: '技能', value: summary.value.skill_count ?? '-', badge: 'SKILL', desc: '可检索能力项' },
  { label: '关系', value: summary.value.graph_relation_count ?? '-', badge: 'GRAPH', desc: '图谱已建立连接' }
])

const workflowSteps = computed(() => [
  { title: '数据入库', desc: '管理招聘平台、企业官网、校招和历史样本', path: isCandidate.value ? '/skill-graph' : '/datasets' },
  { title: 'JD 处理', desc: '提取岗位、职责、技能、工具和证书', path: isCandidate.value ? '/skill-graph' : '/jd-parser' },
  { title: '新岗位', desc: '发现高频新名称和新能力组合', path: isCandidate.value ? '/skill-graph' : '/emerging-jobs' },
  { title: '能力变更', desc: '跟踪岗位要求的新增、移除和调整', path: isCandidate.value ? '/skill-graph' : '/job-evolution' },
  { title: '图谱查看', desc: '查看岗位、技能、证书、课程和场景', path: '/skill-graph' },
  { title: '匹配分析', desc: '对比简历与目标岗位，生成差距清单', path: '/match-analysis' }
])

const qualityMetrics = computed(() => [
  { label: 'JD 解析准确率', value: summary.value.jd_parse_accuracy ?? 0 },
  { label: '简历解析准确率', value: summary.value.resume_parse_accuracy ?? 0 },
  { label: '匹配准确率', value: summary.value.match_accuracy ?? 0 },
  { label: '单元测试覆盖率', value: summary.value.unit_test_coverage ?? 0 }
])

const roleTasks = computed(() =>
  isCandidate.value
    ? [
        { title: '完善资料', desc: '补齐学历、城市、薪资、能力和证书', path: '/personal-center' },
        { title: '解析简历', desc: '提取教育、项目、技能和岗位意向', path: '/resume-parser' },
        { title: '查看差距', desc: '选择目标岗位，查看匹配结果', path: '/match-analysis' },
        { title: '练习面试', desc: '围绕目标岗位准备问答', path: '/digital-interviewer' }
      ]
    : [
        { title: '检查数据源', desc: '查看重复率、噪声率和处理状态', path: '/datasets' },
        { title: '核验新岗位', desc: '查看候选岗位、技能和来源', path: '/emerging-jobs' },
        { title: '维护能力项', desc: '确认岗位能力的变化记录', path: '/job-evolution' },
        { title: '处理审核', desc: '通过或驳回待复核内容', path: '/review-tasks' }
      ]
)

const trendOption = computed(() => ({
  color: ['#2563eb', '#06b6d4', '#18b981'],
  tooltip: { trigger: 'axis' },
  legend: {
    top: 4,
    textStyle: { color: '#53657e', fontWeight: 700 },
    data: ['JD', '技能', '更新']
  },
  grid: { left: 38, right: 22, top: 48, bottom: 34 },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    axisLine: { lineStyle: { color: '#bed5f2' } },
    axisLabel: { color: '#64748b' },
    data: (summary.value.trend || []).map((i: any) => i.date)
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: 'rgba(190,213,242,.55)' } },
    axisLabel: { color: '#64748b' }
  },
  series: [
    { name: 'JD', type: 'line', smooth: true, symbol: 'circle', symbolSize: 7, areaStyle: { opacity: 0.14 }, data: (summary.value.trend || []).map((i: any) => i.jd) },
    { name: '技能', type: 'line', smooth: true, symbol: 'circle', symbolSize: 7, areaStyle: { opacity: 0.12 }, data: (summary.value.trend || []).map((i: any) => i.skills) },
    { name: '更新', type: 'bar', barWidth: 10, itemStyle: { borderRadius: [8, 8, 0, 0] }, data: (summary.value.trend || []).map((i: any) => i.updates) }
  ]
}))

const barOption = computed(() => ({
  tooltip: {},
  grid: { left: 46, right: 18, top: 18, bottom: 30 },
  xAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: 'rgba(190,213,242,.55)' } },
    axisLabel: { color: '#64748b' }
  },
  yAxis: {
    type: 'category',
    axisLine: { lineStyle: { color: '#bed5f2' } },
    axisLabel: { color: '#53657e', fontWeight: 700 },
    data: (summary.value.job_distribution || []).map((i: any) => i.name)
  },
  series: [
    {
      type: 'bar',
      barWidth: 15,
      data: (summary.value.job_distribution || []).map((i: any) => i.value),
      itemStyle: {
        borderRadius: [0, 9, 9, 0],
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 1,
          y2: 0,
          colorStops: [
            { offset: 0, color: '#2563eb' },
            { offset: 1, color: '#06b6d4' }
          ]
        }
      }
    }
  ]
}))

onMounted(async () => {
  summary.value = await api.overview()
})
</script>

<style scoped>
.overview-hero {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 430px;
  gap: 26px;
  overflow: hidden;
  min-height: 272px;
  border: 1px solid rgba(190, 213, 242, 0.86);
  border-radius: 24px;
  padding: 32px;
  background:
    radial-gradient(circle at 18% 4%, rgba(6, 182, 212, 0.2), transparent 28%),
    radial-gradient(circle at 86% 18%, rgba(37, 99, 235, 0.18), transparent 28%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.94), rgba(232, 242, 255, 0.72));
  box-shadow: 0 22px 68px rgba(37, 99, 235, 0.13);
  backdrop-filter: blur(22px);
}

.overview-hero::after {
  position: absolute;
  right: -120px;
  bottom: -150px;
  width: 460px;
  height: 460px;
  content: "";
  border-radius: 50%;
  border: 1px solid rgba(6, 182, 212, 0.24);
  box-shadow: inset 0 0 80px rgba(6, 182, 212, 0.12);
}

.hero-copy {
  position: relative;
  z-index: 1;
}

.hero-kicker {
  display: inline-flex;
  border: 1px solid rgba(6, 182, 212, 0.28);
  border-radius: 999px;
  padding: 7px 12px;
  background: rgba(231, 251, 255, 0.68);
  color: #0891b2;
  font-size: 12px;
  font-weight: 950;
}

.hero-copy h1 {
  max-width: 760px;
  margin: 18px 0 12px;
  color: #071a3d;
  font-size: 34px;
  font-weight: 950;
  line-height: 1.25;
}

.hero-copy p {
  max-width: 860px;
  margin: 0;
  color: #53657e;
  font-size: 15px;
  font-weight: 650;
  line-height: 1.9;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 24px;
}

.hero-network {
  position: relative;
  min-height: 230px;
}

.orbit {
  position: absolute;
  left: 50%;
  top: 50%;
  border-radius: 50%;
  transform: translate(-50%, -50%);
}

.orbit-outer {
  width: 248px;
  height: 248px;
  border: 1px solid rgba(37, 99, 235, 0.22);
  box-shadow: inset 0 0 36px rgba(6, 182, 212, 0.08);
}

.orbit-inner {
  width: 178px;
  height: 178px;
  border: 1px dashed rgba(6, 182, 212, 0.42);
  animation: rotateOrbit 12s linear infinite;
}

.network-core {
  position: absolute;
  left: 50%;
  top: 50%;
  display: grid;
  place-items: center;
  width: 138px;
  height: 138px;
  border: 1px solid rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  background:
    radial-gradient(circle at 38% 24%, rgba(255, 255, 255, 0.92), transparent 24%),
    linear-gradient(135deg, #2563eb, #06b6d4);
  box-shadow: 0 0 42px rgba(6, 182, 212, 0.32);
  color: #fff;
  transform: translate(-50%, -50%);
}

.network-core span {
  font-size: 38px;
  font-weight: 950;
  line-height: 1;
}

.network-core b {
  margin-top: -24px;
  font-size: 13px;
}

.node {
  position: absolute;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 0 0 6px rgba(6, 182, 212, 0.13), 0 0 28px rgba(6, 182, 212, 0.48);
}

.node-a { left: 54px; top: 36px; }
.node-b { right: 42px; top: 52px; }
.node-c { left: 78px; bottom: 42px; }
.node-d { right: 82px; bottom: 36px; }

.link {
  position: absolute;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(37, 99, 235, 0.32), rgba(6, 182, 212, 0.42), transparent);
  transform-origin: left center;
}

.link-a { left: 72px; top: 64px; width: 276px; transform: rotate(8deg); }
.link-b { left: 98px; bottom: 62px; width: 240px; transform: rotate(-12deg); }
.link-c { left: 104px; top: 118px; width: 245px; transform: rotate(38deg); }

.overview-metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.overview-metric {
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(190, 213, 242, 0.86);
  border-radius: 22px;
  padding: 18px;
  background: rgba(255, 255, 255, 0.74);
  box-shadow: 0 18px 48px rgba(37, 99, 235, 0.1);
  transition: transform 220ms ease, box-shadow 220ms ease, border-color 220ms ease;
}

.overview-metric:hover,
.workflow-step:hover {
  border-color: rgba(6, 182, 212, 0.46);
  box-shadow: 0 24px 66px rgba(37, 99, 235, 0.16);
  transform: translateY(-3px);
}

.metric-top {
  display: flex;
  justify-content: space-between;
  color: #64748b;
  font-size: 13px;
  font-weight: 900;
}

.metric-top em {
  color: var(--cyan);
  font-style: normal;
  letter-spacing: 0.12em;
}

.overview-metric strong {
  display: block;
  margin-top: 16px;
  color: #071a3d;
  font-size: 34px;
  font-weight: 950;
}

.overview-metric small {
  display: block;
  margin-top: 9px;
  color: #64748b;
  font-weight: 750;
}

.workflow-panel {
  grid-column: span 12;
}

.workflow-lane {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 12px;
}

.workflow-step {
  position: relative;
  min-height: 138px;
  border: 1px solid rgba(190, 213, 242, 0.82);
  border-radius: 18px;
  padding: 16px;
  background:
    radial-gradient(circle at 12% 0%, rgba(6, 182, 212, 0.16), transparent 34%),
    rgba(255, 255, 255, 0.68);
  color: #14346c;
  text-align: left;
  cursor: pointer;
  transition: transform 220ms ease, box-shadow 220ms ease, border-color 220ms ease;
}

.workflow-step span {
  display: inline-grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border-radius: 13px;
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.14), rgba(6, 182, 212, 0.16));
  color: #1455b8;
  font-size: 12px;
  font-weight: 950;
}

.workflow-step b {
  display: block;
  margin-top: 13px;
  color: #071a3d;
  font-size: 15px;
  font-weight: 950;
}

.workflow-step small {
  display: block;
  margin-top: 8px;
  color: #64748b;
  font-size: 12px;
  font-weight: 700;
  line-height: 1.65;
}

.panel-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.panel-heading h3 {
  margin: 0;
}

.panel-heading p {
  margin: 6px 0 0;
  color: #64748b;
  font-size: 13px;
  font-weight: 700;
}

.quality-list {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding-top: 8px;
}

.quality-item > div {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  color: #53657e;
  font-weight: 850;
}

.quality-item b {
  color: #071a3d;
}

.graph-status {
  display: grid;
  gap: 12px;
}

.graph-status > div {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border: 1px solid rgba(190, 213, 242, 0.8);
  border-radius: 16px;
  padding: 14px;
  background: rgba(232, 242, 255, 0.52);
}

.graph-status span {
  color: #64748b;
  font-weight: 850;
}

.graph-status b {
  color: #0f2f78;
  font-size: 24px;
  font-weight: 950;
}

.task-list {
  display: grid;
  gap: 12px;
}

.task-list button {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  border: 1px solid rgba(190, 213, 242, 0.82);
  border-radius: 16px;
  padding: 13px;
  background: rgba(255, 255, 255, 0.6);
  color: #14346c;
  cursor: pointer;
  transition: all 180ms ease;
}

.task-list button:hover {
  border-color: rgba(6, 182, 212, 0.45);
  background: rgba(231, 251, 255, 0.68);
  transform: translateY(-2px);
}

.task-list span {
  font-weight: 950;
}

.task-list small {
  margin-top: 6px;
  color: #64748b;
  font-weight: 700;
}

.guard-panel {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  background:
    radial-gradient(circle at 8% 20%, rgba(6, 182, 212, 0.14), transparent 28%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.88), rgba(232, 242, 255, 0.68));
}

.guard-panel h3 {
  margin: 0 0 8px;
}

.guard-panel p {
  margin: 0;
  color: #53657e;
  font-weight: 700;
}

@keyframes rotateOrbit {
  to {
    transform: translate(-50%, -50%) rotate(360deg);
  }
}
</style>
