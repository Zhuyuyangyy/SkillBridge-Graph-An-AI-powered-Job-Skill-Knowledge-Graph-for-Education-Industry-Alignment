<template>
  <div class="page digital-page">
    <PageHeader title="数字人面试官" desc="围绕目标岗位进行结构化追问、表达反馈和能力评分，支持视频、语音识别、语音合成与数字人驱动">
      <div class="toolbar">
        <el-select v-model="jobName" placeholder="选择面试岗位" style="width: 240px">
          <el-option v-for="job in jobs" :key="job.id" :label="job.name" :value="job.name" />
        </el-select>
        <el-button type="primary" :loading="loading" @click="startInterview">开始/生成下一题</el-button>
      </div>
    </PageHeader>

    <div class="content-grid">
      <section class="panel span-5 avatar-panel">
        <div class="avatar-stage">
          <div class="avatar-halo"></div>
          <div class="digital-avatar">
            <div class="avatar-face">
              <span class="eye left"></span>
              <span class="eye right"></span>
              <span class="mouth"></span>
            </div>
            <div class="avatar-body"></div>
          </div>
          <div class="voice-wave">
            <i v-for="item in 18" :key="item"></i>
          </div>
        </div>
        <div class="sdk-grid">
          <div v-for="item in sdkItems" :key="item.label">
            <b>{{ item.label }}</b>
            <span>{{ item.value }}</span>
          </div>
        </div>
      </section>

      <section class="panel span-7 interview-panel">
        <div class="panel-heading">
          <div>
            <h3>面试对话</h3>
            <p>基于岗位画像、简历摘要和候选人回答生成追问、反馈和评分</p>
          </div>
          <el-tag type="primary">{{ providerLabel }}</el-tag>
        </div>

        <div class="chat-stream">
          <div class="message interviewer">
            <span>数字人面试官</span>
            <p>{{ result?.next_question || '请选择目标岗位，点击开始面试。' }}</p>
          </div>
          <div class="message candidate">
            <span>候选人回答</span>
            <el-input v-model="candidateAnswer" type="textarea" :rows="5" placeholder="这里输入候选人的回答；接入语音识别后也可以自动转写。" />
          </div>
        </div>

        <div class="interview-actions">
          <el-button @click="candidateAnswer = ''">清空回答</el-button>
          <el-button type="primary" :loading="loading" @click="startInterview">提交回答并追问</el-button>
        </div>
      </section>

      <section class="panel span-4">
        <h3>简历摘要</h3>
        <el-input v-model="resumeSummary" type="textarea" :rows="10" placeholder="粘贴简历摘要，也可从简历解析结果自动带入。" />
      </section>

      <section class="panel span-4">
        <h3>评分预览</h3>
        <div class="score-list">
          <div v-for="(score, name) in result?.score_preview || defaultScores" :key="name">
            <span>{{ name }}</span>
            <el-progress :percentage="score" :stroke-width="10" />
          </div>
        </div>
      </section>

      <section class="panel span-4">
        <h3>面试反馈</h3>
        <p class="feedback">{{ result?.feedback || '等待候选人回答后生成反馈。' }}</p>
        <div class="tag-list">
          <el-tag v-for="tag in result?.follow_up_tags || ['追问策略', '语音识别', 'TTS', '数字人驱动']" :key="tag" type="info">{{ tag }}</el-tag>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import { api } from '@/api/http'

const jobs = ref<any[]>([])
const jobName = ref('')
const resumeSummary = ref('本科计算机相关专业，熟悉 Python、SQL、RAG、项目管理，参与过知识库问答和数据分析项目。')
const candidateAnswer = ref('')
const response = ref<any>()
const loading = ref(false)

const result = computed(() => response.value?.result)
const providerLabel = computed(() => (response.value?.provider === 'mock' ? '本地智能服务' : response.value?.provider || '智能服务'))
const defaultScores = {
  专业能力: 0,
  项目表达: 0,
  岗位匹配: 0,
  逻辑沟通: 0
}

const sdkItems = computed(() => {
  const sdk = result.value?.sdk_placeholder || {}
  return [
    { label: '视频流', value: formatSdkState(sdk.video_stream) },
    { label: '语音识别', value: formatSdkState(sdk.asr) },
    { label: '语音合成', value: formatSdkState(sdk.tts) },
    { label: '数字人驱动', value: formatSdkState(sdk.avatar_driver) }
  ]
})

function formatSdkState(value?: string) {
  if (!value || value === 'reserved' || value === 'interface-ready') return '已就绪'
  return value
}

async function startInterview() {
  if (!jobName.value) {
    ElMessage.warning('请先选择面试岗位')
    return
  }
  loading.value = true
  try {
    response.value = await api.digitalInterview({
      job_name: jobName.value,
      resume_summary: resumeSummary.value,
      candidate_answer: candidateAnswer.value,
      stage: candidateAnswer.value ? 'follow_up' : 'opening'
    })
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  jobs.value = await api.jobs()
  jobName.value = jobs.value[0]?.name || ''
})
</script>

<style scoped>
.avatar-panel {
  min-height: 560px;
}

.avatar-stage {
  position: relative;
  display: grid;
  place-items: center;
  height: 360px;
  overflow: hidden;
  border: 1px solid rgba(37, 99, 235, 0.24);
  border-radius: 22px;
  background:
    linear-gradient(rgba(37, 99, 235, 0.055) 1px, transparent 1px),
    linear-gradient(90deg, rgba(37, 99, 235, 0.055) 1px, transparent 1px),
    radial-gradient(circle at 50% 22%, rgba(6, 182, 212, 0.22), transparent 30%),
    linear-gradient(135deg, rgba(248, 251, 255, 0.94), rgba(231, 244, 255, 0.82));
  background-size: 34px 34px, 34px 34px, auto, auto;
}

.avatar-halo {
  position: absolute;
  width: 230px;
  height: 230px;
  border-radius: 50%;
  border: 1px solid rgba(6, 182, 212, 0.35);
  box-shadow: 0 0 80px rgba(6, 182, 212, 0.18), inset 0 0 60px rgba(37, 99, 235, 0.1);
  animation: haloPulse 4.8s ease-in-out infinite;
}

.avatar-halo::after {
  position: absolute;
  inset: 26px;
  content: "";
  border-radius: 50%;
  border: 1px dashed rgba(37, 99, 235, 0.28);
  animation: haloSpin 14s linear infinite;
}

.digital-avatar {
  position: relative;
  z-index: 1;
  display: grid;
  place-items: center;
}

.avatar-face {
  position: relative;
  width: 132px;
  height: 132px;
  border-radius: 48% 52% 46% 54%;
  background:
    radial-gradient(circle at 35% 24%, rgba(255, 255, 255, 0.95), transparent 25%),
    linear-gradient(135deg, #2563eb, #06b6d4);
  box-shadow: 0 18px 42px rgba(37, 99, 235, 0.24);
}

.eye {
  position: absolute;
  top: 48px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 0 16px rgba(255, 255, 255, 0.86);
}

.eye.left {
  left: 38px;
}

.eye.right {
  right: 38px;
}

.mouth {
  position: absolute;
  left: 48px;
  bottom: 36px;
  width: 36px;
  height: 9px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.85);
}

.avatar-body {
  width: 182px;
  height: 92px;
  margin-top: -18px;
  border-radius: 70px 70px 24px 24px;
  background: linear-gradient(135deg, rgba(15, 47, 120, 0.88), rgba(6, 182, 212, 0.72));
  box-shadow: 0 18px 42px rgba(37, 99, 235, 0.22);
}

.voice-wave {
  position: absolute;
  right: 28px;
  bottom: 28px;
  display: flex;
  align-items: end;
  gap: 4px;
  height: 52px;
}

.voice-wave i {
  width: 4px;
  height: 16px;
  border-radius: 99px;
  background: linear-gradient(180deg, var(--cyan), var(--primary));
  animation: wave 1.2s ease-in-out infinite;
}

.voice-wave i:nth-child(2n) {
  animation-delay: 120ms;
}

.voice-wave i:nth-child(3n) {
  animation-delay: 240ms;
}

@keyframes wave {
  0%, 100% { height: 14px; opacity: 0.45; }
  50% { height: 48px; opacity: 1; }
}

@keyframes haloPulse {
  0%, 100% { transform: scale(0.98); opacity: 0.78; }
  50% { transform: scale(1.04); opacity: 1; }
}

@keyframes haloSpin {
  to { transform: rotate(360deg); }
}

.sdk-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.sdk-grid > div {
  border: 1px solid rgba(190, 213, 242, 0.82);
  border-radius: 16px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.6);
}

.sdk-grid b {
  display: block;
  color: #14346c;
  font-size: 12px;
}

.sdk-grid span {
  display: block;
  margin-top: 6px;
  color: var(--cyan);
  font-size: 12px;
  font-weight: 900;
}

.chat-stream {
  display: grid;
  gap: 14px;
}

.message {
  border: 1px solid rgba(190, 213, 242, 0.82);
  border-radius: 18px;
  padding: 14px;
  background: rgba(255, 255, 255, 0.6);
}

.message span {
  color: var(--cyan);
  font-size: 12px;
  font-weight: 950;
}

.message p {
  margin: 8px 0 0;
  color: #1e293b;
  line-height: 1.8;
}

.interview-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 14px;
}

.score-list {
  display: grid;
  gap: 16px;
}

.score-list span {
  display: block;
  margin-bottom: 8px;
  color: #53657e;
  font-weight: 850;
}

.feedback {
  color: #334155;
  line-height: 1.9;
}
</style>
