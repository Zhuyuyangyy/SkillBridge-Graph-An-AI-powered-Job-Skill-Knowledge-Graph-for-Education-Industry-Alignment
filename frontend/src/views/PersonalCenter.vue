<template>
  <div class="page profile-page">
    <section class="profile-card profile-glass-card">
      <div class="profile-identity">
        <button class="avatar-picker" type="button" @click="chooseAvatar">
          <img v-if="profile.avatar_url" :src="profile.avatar_url" alt="个人头像" />
          <span v-else class="avatar-icon-wrap">
            <IconSprite name="profile" :size="68" />
            <b>{{ avatarInitial }}</b>
          </span>
        </button>
        <div class="identity-copy">
          <div class="identity-topline">
            <h2>{{ profile.real_name || auth.user?.display_name || auth.user?.username }}</h2>
            <span>求职者/学生</span>
          </div>
          <p class="identity-summary">{{ profileBrief }}</p>
          <div class="identity-targets">
            <span>目标岗位：{{ profile.target_role || '待选择' }}</span>
            <span>意向城市：{{ cityText || '待选择' }}</span>
          </div>
          <div class="avatar-actions">
            <el-button size="small" @click="chooseAvatar">更换头像</el-button>
            <el-button v-if="profile.avatar_url" size="small" text @click="profile.avatar_url = ''">移除</el-button>
          </div>
          <input ref="avatarInput" class="avatar-input" type="file" accept="image/png,image/jpeg,image/webp" @change="handleAvatarFile" />
        </div>
      </div>

      <div class="profile-card-side">
        <div class="completion-panel">
          <div class="completion-ring" :style="completionStyle">
            <span class="completion-stream stream-1"></span>
            <span class="completion-stream stream-2"></span>
            <span class="completion-stream stream-3"></span>
            <span class="completion-stream stream-4"></span>
            <span class="completion-progress"></span>
            <div class="completion-core">
              <strong>{{ completionPercent }}%</strong>
            </div>
          </div>
          <span>画像完整度</span>
        </div>
        <el-button class="profile-save-btn" type="primary" :loading="saving" @click="saveProfile">保存个人画像</el-button>
      </div>
    </section>

    <section class="profile-flow">
      <article class="profile-flow-summary profile-glass-card">
        <svg class="flow-aurora-svg" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
          <defs>
            <linearGradient id="flowAuroraGradient" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="100" y2="100">
              <stop offset="0%" stop-color="#00c8f5" stop-opacity="0.22" />
              <stop offset="24%" stop-color="#4df5ff" stop-opacity="0.72" />
              <stop offset="50%" stop-color="#1e7bff" stop-opacity="0.82" />
              <stop offset="76%" stop-color="#7c3aed" stop-opacity="0.58" />
              <stop offset="100%" stop-color="#00e5ff" stop-opacity="0.22" />
            </linearGradient>
            <filter id="flowAuroraGlow" x="-30%" y="-30%" width="160%" height="160%">
              <feGaussianBlur stdDeviation="2.6" />
            </filter>
          </defs>
          <rect class="flow-border-base" x="0.8" y="0.8" width="98.4" height="98.4" rx="9" ry="9" />
          <rect class="flow-aurora-glow" pathLength="100" x="0.8" y="0.8" width="98.4" height="98.4" rx="9" ry="9" />
          <rect class="flow-aurora-streak" pathLength="100" x="1" y="1" width="98" height="98" rx="8" ry="8" />
        </svg>
        <span>求职闭环</span>
        <h3>{{ nextAction.title }}</h3>
        <p>{{ nextAction.desc }}</p>
      </article>
      <button v-for="item in flowSteps" :key="item.path" type="button" class="profile-flow-card profile-glass-card" @click="router.push(item.path)">
        <svg class="flow-aurora-svg" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
          <defs>
            <linearGradient id="flowAuroraGradient" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="100" y2="100">
              <stop offset="0%" stop-color="#00c8f5" stop-opacity="0.22" />
              <stop offset="24%" stop-color="#4df5ff" stop-opacity="0.72" />
              <stop offset="50%" stop-color="#1e7bff" stop-opacity="0.82" />
              <stop offset="76%" stop-color="#7c3aed" stop-opacity="0.58" />
              <stop offset="100%" stop-color="#00e5ff" stop-opacity="0.22" />
            </linearGradient>
            <filter id="flowAuroraGlow" x="-30%" y="-30%" width="160%" height="160%">
              <feGaussianBlur stdDeviation="2.6" />
            </filter>
          </defs>
          <rect class="flow-border-base" x="0.8" y="0.8" width="98.4" height="98.4" rx="9" ry="9" />
          <rect class="flow-aurora-glow" pathLength="100" x="0.8" y="0.8" width="98.4" height="98.4" rx="9" ry="9" />
          <rect class="flow-aurora-streak" pathLength="100" x="1" y="1" width="98" height="98" rx="8" ry="8" />
        </svg>
        <span class="flow-arrow">→</span>
        <span class="flow-icon">
          <IconSprite :name="item.icon" :size="118" />
        </span>
        <b>{{ item.index }}</b>
        <strong>{{ item.title }}</strong>
        <em>{{ item.desc }}</em>
      </button>
    </section>

    <section class="profile-status-grid">
      <article v-for="item in qualityItems" :key="item.label" class="profile-status-card profile-glass-card" :class="{ done: item.done }">
        <span class="status-icon">
          <IconSprite :name="item.icon" :size="78" />
        </span>
        <div>
          <b>{{ item.label }}</b>
          <strong>{{ item.done ? '已完善' : '待完善' }}</strong>
        </div>
        <span class="status-check">✓</span>
      </article>
    </section>

    <div class="profile-info-grid">
      <section class="profile-section-card profile-glass-card profile-basic-card">
        <div class="section-head">
          <div>
            <span>BASIC INFORMATION</span>
            <h3>基础信息</h3>
          </div>
          <el-button class="profile-secondary-btn" size="small" @click="focusBasicForm">编辑</el-button>
        </div>
        <el-form label-width="90px">
          <el-form-item label="真实姓名"><el-input v-model="profile.real_name" /></el-form-item>
          <el-form-item label="学历">
            <el-select v-model="profile.education" placeholder="请选择最高学历" filterable>
              <el-option v-for="item in educationOptions" :key="item" :label="item" :value="item" />
            </el-select>
          </el-form-item>
          <el-form-item label="专业"><el-input v-model="profile.major" /></el-form-item>
          <el-form-item label="学校">
            <div class="school-field">
              <el-autocomplete
                v-model="profile.school"
                :fetch-suggestions="querySchools"
                clearable
                placeholder="输入学校名称"
              />
              <div class="school-badges">
                <span v-for="badge in schoolBadges" :key="badge" class="elite-badge" :class="eliteBadgeClass(badge)">{{ badge }}</span>
              </div>
            </div>
          </el-form-item>
          <el-form-item label="目标岗位">
            <el-select v-model="profile.target_role" filterable allow-create default-first-option placeholder="从岗位库选择，也可输入自定义岗位">
              <el-option v-for="item in jobOptions" :key="item" :label="item" :value="item" />
            </el-select>
          </el-form-item>
          <el-form-item label="意向城市">
            <el-cascader
              v-model="locationValue"
              :options="cityOptions"
              filterable
              clearable
              placeholder="请选择省份 / 城市"
            />
          </el-form-item>
          <el-form-item label="期望薪资">
            <div class="salary-range">
              <el-select v-model="salaryStart" filterable placeholder="最低">
                <el-option v-for="item in salaryOptions" :key="`start-${item}`" :label="`${item}k`" :value="item" />
              </el-select>
              <span>至</span>
              <el-select v-model="salaryEnd" filterable placeholder="最高">
                <el-option v-for="item in salaryEndOptions" :key="`end-${item}`" :label="`${item}k`" :value="item" />
              </el-select>
              <em>单位：k / 月</em>
            </div>
          </el-form-item>
        </el-form>
      </section>

      <section class="profile-section-card profile-glass-card profile-ability-card">
        <div class="section-head">
          <div>
            <span>ABILITIES & CERTIFICATES</span>
            <h3>能力与证书</h3>
          </div>
          <el-button class="profile-secondary-btn" size="small" @click="focusAbilityForm">编辑</el-button>
        </div>
        <el-form label-position="top">
          <el-form-item label="我拥有的能力">
            <el-select
              v-model="profile.skills"
              multiple
              filterable
              allow-create
              collapse-tags
              collapse-tags-tooltip
              :max-collapse-tags="4"
              default-first-option
              placeholder="搜索技能、工具、方向或自定义输入"
            >
              <el-option-group v-for="group in skillGroups" :key="group.label" :label="group.label">
                <el-option v-for="item in group.options" :key="item" :label="item" :value="item" />
              </el-option-group>
            </el-select>
            <div v-if="profile.skills.length" class="chip-preview">
              <span v-for="item in profile.skills.slice(0, 8)" :key="item" class="profile-chip">{{ item }}</span>
              <span v-if="profile.skills.length > 8" class="profile-chip more-chip">+{{ profile.skills.length - 8 }}</span>
            </div>
            <div class="select-meta">已内置 {{ skillOptions.length }} 项能力标签，覆盖开发、数据、智能应用、安全、交付和通用能力。</div>
          </el-form-item>
          <el-form-item label="证书">
            <el-select
              v-model="profile.certificates"
              multiple
              filterable
              allow-create
              collapse-tags
              collapse-tags-tooltip
              :max-collapse-tags="3"
              default-first-option
              placeholder="搜索证书名称、厂商或方向，也可自定义输入"
            >
              <el-option-group v-for="group in certificateGroups" :key="group.label" :label="group.label">
                <el-option v-for="item in group.options" :key="item" :label="item" :value="item" />
              </el-option-group>
            </el-select>
            <div v-if="profile.certificates.length" class="chip-preview">
              <span v-for="item in profile.certificates.slice(0, 6)" :key="item" class="profile-chip certificate-chip">{{ item }}</span>
              <span v-if="profile.certificates.length > 6" class="profile-chip more-chip">+{{ profile.certificates.length - 6 }}</span>
            </div>
            <div class="select-meta">已内置 {{ certificateOptions.length }} 项 IT 相关证书，支持关键词搜索和自定义添加。</div>
          </el-form-item>
          <el-form-item label="自我总结">
            <el-input v-model="profile.self_summary" type="textarea" :rows="5" />
          </el-form-item>
        </el-form>
      </section>
    </div>

    <section class="profile-experience-grid">
      <article class="profile-section-card profile-glass-card experience-card">
        <div class="experience-head">
          <span class="experience-icon">
            <IconSprite name="folder" :size="86" />
          </span>
          <div>
            <span>PROJECT EXPERIENCE</span>
            <h3>项目经历</h3>
            <p>写清项目目标、你的职责、技术栈和结果。</p>
          </div>
          <b>{{ profile.projects.length }} 项</b>
        </div>
        <TagEditor v-model="profile.projects" placeholder="例如：岗位能力图谱平台，负责图谱关系建模与可视化" empty-text="还没有项目经历，建议补充 1-3 个能证明能力的项目。" />
      </article>

      <article class="profile-section-card profile-glass-card experience-card">
        <div class="experience-head">
          <span class="experience-icon">
            <IconSprite name="shield" :size="86" />
          </span>
          <div>
            <span>INTERNSHIP EXPERIENCE</span>
            <h3>实习经历</h3>
            <p>记录公司、岗位、工作内容和产出。</p>
          </div>
          <b>{{ profile.internships.length }} 项</b>
        </div>
        <TagEditor v-model="profile.internships" placeholder="例如：某科技公司数据平台实习，参与指标口径治理" empty-text="还没有实习经历，可以先写课程实践、实验室经历或校企项目。" />
      </article>

      <article class="profile-section-card profile-glass-card experience-card">
        <div class="experience-head">
          <span class="experience-icon">
            <IconSprite name="certificate" :size="86" />
          </span>
          <div>
            <span>COMPETITIONS & AWARDS</span>
            <h3>竞赛 / 奖项</h3>
            <p>补充证书、竞赛、奖学金或作品成果。</p>
          </div>
          <b>{{ profile.awards.length }} 项</b>
        </div>
        <TagEditor v-model="profile.awards" placeholder="例如：大学生软件设计竞赛省级二等奖" empty-text="还没有竞赛或奖项，后续可补充证书、比赛、论文或作品成果。" />
      </article>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, h, onMounted, reactive, ref, watch } from 'vue'
import { ElButton, ElInput, ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import IconSprite from '@/components/IconSprite.vue'
import { api } from '@/api/http'
import { useAuthStore } from '@/stores/auth'
import { certificateGroups, certificateOptions } from '@/data/certificates'
import { cityOptions, doubleFirstClassUniversities, educationOptions, eliteUniversityOptions, salaryOptions, universities211, universities985 } from '@/data/profileOptions'
import { skillGroups, skillOptions } from '@/data/skills'

type SpriteName = 'profile' | 'progress' | 'certificate' | 'folder' | 'target' | 'chart' | 'education' | 'shield' | 'setting'

const auth = useAuthStore()
const router = useRouter()
const saving = ref(false)
const avatarInput = ref<HTMLInputElement>()
const locationValue = ref<string[]>([])
const salaryStart = ref<number>()
const salaryEnd = ref<number>()
const jobs = ref<any[]>([])
const profile = reactive<any>({
  real_name: '',
  education: '',
  major: '',
  school: '',
  target_role: '',
  city: '',
  expected_salary: '',
  avatar_url: '',
  skills: [],
  certificates: [],
  projects: [],
  internships: [],
  awards: [],
  self_summary: '',
  completeness: 0
})

const avatarInitial = computed(() => (profile.real_name || auth.user?.display_name || auth.user?.username || '我').slice(0, 1))
const completionPercent = computed(() => Number(profile.completeness || 0).toFixed(1).replace(/\.0$/, ''))
const completionStyle = computed(() => {
  const degree = Math.max(0, Math.min(100, Number(profile.completeness || 0))) * 3.6
  return { '--completion-degree': `${degree}deg` }
})
const profileBrief = computed(() => {
  const fields = [profile.major, profile.education, profile.school].filter(Boolean)
  return fields.length ? fields.join(' · ') : '补充专业、学历和学校后，画像摘要会在这里展示'
})
const cityText = computed(() => formatLocation() || profile.city)
const schoolBadges = computed(() => {
  const normalized = normalizeSchoolName(profile.school)
  const badges: string[] = []
  if (universities985.some((name) => normalizeSchoolName(name) === normalized)) badges.push('985')
  if (badges.includes('985') || universities211.some((name) => normalizeSchoolName(name) === normalized)) badges.push('211')
  if (doubleFirstClassUniversities.some((name) => normalizeSchoolName(name) === normalized)) badges.push('双一流')
  return badges
})
const salaryEndOptions = computed(() => salaryOptions.filter((item) => !salaryStart.value || item >= salaryStart.value))
const jobOptions = computed(() => Array.from(new Set(jobs.value.map((item) => item.name).filter(Boolean))))
const qualityItems = computed<{ label: string; icon: SpriteName; done: boolean }[]>(() => [
  { label: '基础信息', icon: 'profile', done: Boolean(profile.real_name && profile.education && profile.school && profile.major) },
  { label: '求职意向', icon: 'target', done: Boolean(profile.target_role && profile.city && profile.expected_salary) },
  { label: '能力标签', icon: 'shield', done: profile.skills.length >= 5 },
  { label: '证书成果', icon: 'certificate', done: Boolean(profile.certificates.length || profile.awards.length) },
  { label: '项目证据', icon: 'folder', done: Boolean(profile.projects.length || profile.internships.length) },
  { label: '个人总结', icon: 'chart', done: Boolean(profile.self_summary) }
])
const nextAction = computed(() => {
  const missing = qualityItems.value.find((item) => !item.done)
  if (missing) {
    return {
      title: `建议先完善：${missing.label}`,
      desc: '补齐这些信息后，岗位匹配、学习路径和面试练习会更贴近你的实际经历。'
    }
  }
  return {
    title: '画像已具备匹配分析条件',
    desc: '现在可以查看目标岗位差距，再安排学习计划和面试练习。'
  }
})
const flowSteps: Array<{ index: string; title: string; desc: string; path: string; icon: SpriteName }> = [
  { index: '01', title: '解析简历', desc: '提取教育、项目、技能和证书信息', path: '/resume-parser', icon: 'certificate' },
  { index: '02', title: '完善画像', desc: '选择城市、薪资和能力材料', path: '/personal-center', icon: 'profile' },
  { index: '03', title: '人岗匹配', desc: '查看总分、差距和风险点', path: '/match-analysis', icon: 'target' },
  { index: '04', title: '学习路径', desc: '按缺失技能生成提升路线', path: '/learning-path', icon: 'education' },
  { index: '05', title: '面试练习', desc: '围绕岗位进行追问训练', path: '/digital-interviewer', icon: 'setting' }
]

const TagEditor = {
  props: ['modelValue', 'placeholder', 'emptyText'],
  emits: ['update:modelValue'],
  setup(props: any, { emit }: any) {
    const value = ref('')
    const add = () => {
      if (!value.value.trim()) return
      emit('update:modelValue', [...props.modelValue, value.value.trim()])
      value.value = ''
    }
    const remove = (item: string) => emit('update:modelValue', props.modelValue.filter((v: string) => v !== item))
    return () =>
      h('div', { class: 'tag-editor' }, [
        props.modelValue.length
          ? h('div', { class: 'experience-list' }, props.modelValue.map((item: string, index: number) =>
              h('div', { class: 'experience-item' }, [
                h('span', { class: 'experience-index' }, String(index + 1).padStart(2, '0')),
                h('p', item),
                h(ElButton, { text: true, type: 'primary', onClick: () => remove(item) }, () => '移除')
              ])
            ))
          : h('div', { class: 'experience-empty' }, [
              h('span'),
              h('p', props.emptyText || '暂无记录，补充后会用于画像完整度和匹配分析。')
            ]),
        h('div', { class: 'tag-input-row' }, [
          h(ElInput, { modelValue: value.value, 'onUpdate:modelValue': (v: string) => (value.value = v), placeholder: props.placeholder, onKeyup: (e: KeyboardEvent) => e.key === 'Enter' && add() }),
          h(ElButton, { type: 'primary', onClick: add }, () => '添加')
        ])
      ])
  }
}

async function loadProfile() {
  const [profileData, jobRows] = await Promise.all([api.myProfile(), api.jobs()])
  Object.assign(profile, profileData)
  jobs.value = jobRows
  locationValue.value = parseLocation(profile.city)
  const salary = parseSalary(profile.expected_salary)
  salaryStart.value = salary[0]
  salaryEnd.value = salary[1]
}

async function saveProfile() {
  saving.value = true
  try {
    profile.city = formatLocation()
    profile.expected_salary = formatSalary()
    Object.assign(profile, await api.updateMyProfile(profile))
    window.dispatchEvent(new CustomEvent('profile-avatar-updated', { detail: { avatar_url: profile.avatar_url } }))
    ElMessage.success('个人画像已保存')
  } finally {
    saving.value = false
  }
}

watch(salaryStart, (value) => {
  if (value && salaryEnd.value && salaryEnd.value < value) salaryEnd.value = value
})

function querySchools(query: string, callback: (items: { value: string }[]) => void) {
  const keyword = normalizeSchoolName(query)
  callback(eliteUniversityOptions.filter((item) => !keyword || normalizeSchoolName(item.value).includes(keyword)).slice(0, 20))
}

function normalizeSchoolName(value = '') {
  return value.replace(/[（(].*?[）)]/g, '').replace(/\s+/g, '').trim()
}

function eliteBadgeClass(badge: string) {
  return {
    'elite-badge-985': badge === '985',
    'elite-badge-211': badge === '211',
    'elite-badge-double': badge === '双一流'
  }
}

function parseLocation(value = '') {
  const parts = value.split('/').map((item) => item.trim()).filter(Boolean)
  if (parts.length >= 2) return [parts[0], parts[1]]
  const matchedProvince = cityOptions.find((province) => province.children.some((city) => city.value === value))
  return matchedProvince ? [matchedProvince.value, value] : []
}

function formatLocation() {
  if (!locationValue.value.length) return ''
  const [province, city] = locationValue.value
  if (!city || province === city) return province
  return `${province} / ${city}`
}

function parseSalary(value = ''): [number | undefined, number | undefined] {
  const numbers = value.match(/\d+/g)?.map(Number) || []
  return [numbers[0], numbers[1]]
}

function formatSalary() {
  if (!salaryStart.value && !salaryEnd.value) return ''
  if (salaryStart.value && salaryEnd.value) return `${salaryStart.value}k-${salaryEnd.value}k`
  return salaryStart.value ? `${salaryStart.value}k起` : `${salaryEnd.value}k以内`
}

function chooseAvatar() {
  avatarInput.value?.click()
}

function handleAvatarFile(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  if (!file.type.startsWith('image/')) {
    ElMessage.warning('请选择图片文件')
    return
  }
  if (file.size > 1.5 * 1024 * 1024) {
    ElMessage.warning('头像图片建议小于 1.5MB')
    input.value = ''
    return
  }
  const reader = new FileReader()
  reader.onload = () => {
    profile.avatar_url = String(reader.result || '')
  }
  reader.readAsDataURL(file)
  input.value = ''
}

function focusBasicForm() {
  document.querySelector<HTMLInputElement>('.profile-basic-card input')?.focus()
}

function focusAbilityForm() {
  document.querySelector<HTMLInputElement>('.profile-ability-card input')?.focus()
}

onMounted(loadProfile)
</script>

<style scoped>
.profile-page {
  position: relative;
  isolation: isolate;
  display: grid;
  gap: 20px;
  padding-bottom: 24px;
}

.profile-page::before {
  position: absolute;
  z-index: -1;
  inset: -22px;
  content: "";
  border-radius: 28px;
  background:
    radial-gradient(circle at 82% 6%, rgba(55, 139, 255, 0.2), transparent 28%),
    radial-gradient(circle at 18% 24%, rgba(0, 207, 245, 0.14), transparent 26%),
    linear-gradient(180deg, #f6fbff 0%, #eaf4ff 100%);
}

.profile-page::after {
  position: absolute;
  z-index: -1;
  inset: -22px;
  content: "";
  border-radius: 28px;
  background-image:
    repeating-linear-gradient(0deg, rgba(68, 128, 200, 0.08) 0 1px, transparent 1px 36px),
    repeating-linear-gradient(90deg, rgba(68, 128, 200, 0.08) 0 1px, transparent 1px 36px);
  opacity: 0.85;
  pointer-events: none;
}

.profile-glass-card {
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(113, 177, 255, 0.32);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.72);
  box-shadow: 0 18px 50px rgba(24, 96, 188, 0.1);
  backdrop-filter: blur(18px);
  transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease;
}

.profile-glass-card:hover {
  border-color: rgba(56, 146, 255, 0.55);
  box-shadow: 0 22px 60px rgba(24, 96, 188, 0.16);
}

.section-head span,
.profile-flow-summary span,
.experience-head span {
  color: #00aee8;
  font-size: 11px;
  font-weight: 950;
  letter-spacing: 0.14em;
}

.profile-save-btn,
.profile-page :deep(.el-button--primary) {
  border: 0;
  border-radius: 14px;
  background: linear-gradient(135deg, #1e7bff, #00bdeb);
  box-shadow: 0 12px 26px rgba(30, 123, 255, 0.25);
  font-weight: 850;
}

.profile-card {
  display: flex;
  min-height: 178px;
  align-items: center;
  justify-content: space-between;
  gap: 22px;
  padding: 24px 28px;
  background:
    radial-gradient(circle at 88% 12%, rgba(0, 200, 245, 0.14), transparent 28%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.78), rgba(234, 245, 255, 0.68));
}

.profile-identity {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 22px;
}

.avatar-picker {
  position: relative;
  display: grid;
  flex: 0 0 auto;
  place-items: center;
  width: 104px;
  height: 104px;
  overflow: hidden;
  border: 1px solid rgba(89, 172, 255, 0.56);
  border-radius: 28px;
  background:
    radial-gradient(circle at 30% 18%, rgba(255, 255, 255, 0.95), transparent 30%),
    linear-gradient(135deg, #0b2b6f, #1e7bff 58%, #00c8f5);
  box-shadow: 0 20px 48px rgba(30, 123, 255, 0.24);
  color: #fff;
  cursor: pointer;
}

.avatar-picker::after {
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  padding: 6px 0;
  background: rgba(7, 26, 61, 0.7);
  color: #dff8ff;
  content: "更换头像";
  font-size: 11px;
  font-weight: 850;
  opacity: 0;
  transition: opacity 180ms ease;
}

.avatar-picker:hover::after {
  opacity: 1;
}

.avatar-picker img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-icon-wrap {
  position: relative;
  display: grid;
  place-items: center;
}

.avatar-icon-wrap b {
  position: absolute;
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: rgba(6, 20, 52, 0.72);
  color: #fff;
  font-size: 18px;
  font-weight: 950;
}

.identity-copy {
  min-width: 0;
}

.identity-topline {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}

.identity-topline h2 {
  margin: 0;
  color: #071a3d;
  font-size: 28px;
  line-height: 1.2;
}

.identity-topline span {
  border: 1px solid rgba(30, 123, 255, 0.22);
  border-radius: 999px;
  padding: 6px 12px;
  background: rgba(235, 243, 255, 0.88);
  color: #1e63c7;
  font-size: 12px;
  font-weight: 850;
}

.identity-summary {
  margin: 10px 0 12px;
  color: #496487;
  font-size: 15px;
  font-weight: 750;
  line-height: 1.7;
}

.identity-targets {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.identity-targets span {
  border: 1px solid rgba(95, 159, 255, 0.28);
  border-radius: 12px;
  padding: 8px 11px;
  background: rgba(255, 255, 255, 0.58);
  color: #173b73;
  font-size: 13px;
  font-weight: 800;
}

.avatar-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 13px;
}

.avatar-input {
  display: none;
}

.completion-panel {
  display: grid;
  flex: 0 0 auto;
  place-items: center;
  gap: 10px;
  min-width: 172px;
}

.completion-panel > span {
  color: #34537d;
  font-size: 13px;
  font-weight: 850;
}

.completion-ring {
  position: relative;
  display: grid;
  place-items: center;
  width: 142px;
  height: 142px;
  overflow: hidden;
  border-radius: 50%;
  background:
    linear-gradient(#9b59b6, #84cdfa, #5ad1cd);
  box-shadow: 0 0 38px rgba(30, 123, 255, 0.22), inset 0 0 18px rgba(255, 255, 255, 0.82);
}

.completion-ring::before {
  position: absolute;
  z-index: 2;
  inset: 15px;
  content: "";
  border: 6px solid rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: inset 0 0 24px rgba(30, 123, 255, 0.08);
}

.completion-ring::after {
  position: absolute;
  z-index: 1;
  inset: 10px;
  content: "";
  border-radius: 50%;
  background:
    conic-gradient(from -90deg, rgba(30, 123, 255, 0.95) 0 var(--completion-degree), rgba(216, 234, 255, 0.72) var(--completion-degree) 360deg);
  box-shadow:
    inset 0 0 12px rgba(255, 255, 255, 0.72),
    0 0 18px rgba(30, 123, 255, 0.14);
  -webkit-mask: radial-gradient(circle, transparent 0 70%, #000 71% 100%);
  mask: radial-gradient(circle, transparent 0 70%, #000 71% 100%);
}

.completion-stream {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: linear-gradient(#9b59b6, #84cdfa, #5ad1cd);
  animation: completionRotate 1.8s linear infinite;
}

.completion-stream.stream-1 {
  filter: blur(5px);
}

.completion-stream.stream-2 {
  filter: blur(10px);
}

.completion-stream.stream-3 {
  filter: blur(24px);
}

.completion-stream.stream-4 {
  filter: blur(42px);
  opacity: 0.72;
}

.completion-progress {
  display: none;
}

.completion-core {
  position: relative;
  z-index: 4;
  display: grid;
  place-items: center;
  width: 92px;
  height: 92px;
  border: 0;
  border-radius: 50%;
  background:
    radial-gradient(circle at 36% 25%, rgba(255, 255, 255, 1), rgba(255, 255, 255, 0.94) 58%, rgba(232, 243, 255, 0.92));
  box-shadow:
    inset 0 0 18px rgba(30, 123, 255, 0.08),
    0 0 0 1px rgba(255, 255, 255, 0.78);
  color: #0b2b6f;
}

.completion-core strong {
  font-size: 30px;
  font-weight: 950;
  letter-spacing: 0;
}

@keyframes completionRotate {
  to {
    transform: rotate(360deg);
  }
}

.profile-flow {
  display: grid;
  grid-template-columns: 300px repeat(5, minmax(0, 1fr));
  gap: 14px;
}

.profile-flow-summary,
.profile-flow-card,
.profile-status-card,
.profile-section-card {
  padding: 18px;
}

.profile-flow-summary,
.profile-flow-card {
  animation: none;
}

.profile-flow-summary {
  position: relative;
  overflow: hidden;
  min-height: 150px;
  background:
    radial-gradient(circle at 12% 0%, rgba(0, 200, 245, 0.15), transparent 32%),
    rgba(255, 255, 255, 0.66);
}

.profile-flow-summary::after {
  display: none;
}

.profile-flow-summary > *,
.profile-flow-card > * {
  position: relative;
  z-index: 1;
}

.flow-aurora-svg {
  display: none;
}

.flow-border-base {
  fill: none;
  vector-effect: non-scaling-stroke;
  stroke: rgba(30, 123, 255, 0.13);
  stroke-width: 0.7;
}

.flow-aurora-glow,
.flow-aurora-streak {
  fill: none;
  vector-effect: non-scaling-stroke;
  stroke: url("#flowAuroraGradient");
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-dashoffset: 82;
  animation: flowAuroraTravel 4.6s linear infinite;
  mix-blend-mode: screen;
}

.flow-aurora-glow {
  opacity: 0.78;
  stroke-width: 11;
  stroke-dasharray: 22 78;
  filter: url("#flowAuroraGlow");
}

.flow-aurora-streak {
  display: none;
}

.profile-flow-summary h3 {
  margin: 12px 0 8px;
  color: #071a3d;
  font-size: 21px;
  line-height: 1.35;
}

.profile-flow-summary p {
  margin: 0;
  color: #55708f;
  font-size: 13px;
  font-weight: 750;
  line-height: 1.8;
}

.profile-flow-card {
  position: relative;
  min-height: 176px;
  overflow: hidden;
  padding: 14px 18px 17px;
  text-align: left;
  cursor: pointer;
}

.profile-flow-card:hover,
.profile-status-card:hover,
.profile-section-card:hover {
  transform: translateY(-3px);
}

.profile-flow-summary:hover .flow-aurora-glow,
.profile-flow-card:hover .flow-aurora-glow {
  opacity: 0.92;
  stroke-width: 12;
}

.profile-flow-card::after {
  display: none;
}

.flow-arrow {
  position: absolute;
  top: 13px;
  right: 16px;
  color: #1e7bff;
  font-size: 18px;
  font-weight: 950;
}

.flow-icon {
  display: grid;
  place-items: center;
  width: 126px;
  height: 112px;
  margin: -8px auto 4px;
  overflow: hidden;
  border: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
}

.flow-icon :deep(.sprite-icon),
.status-icon :deep(.sprite-icon),
.experience-icon :deep(.sprite-icon) {
  display: block;
  margin: auto;
  filter: drop-shadow(0 14px 22px rgba(30, 123, 255, 0.2));
}

.profile-flow-card b,
.profile-flow-card strong,
.profile-flow-card em {
  display: block;
}

.profile-flow-card b {
  color: #00aee8;
  font-size: 12px;
  font-weight: 950;
}

.profile-flow-card strong {
  margin-top: 7px;
  color: #0b2b6f;
  font-size: 16px;
  line-height: 1.3;
}

.profile-flow-card em {
  margin-top: 7px;
  color: #5b7190;
  font-style: normal;
  font-size: 12px;
  font-weight: 750;
  line-height: 1.55;
}

.profile-status-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 14px;
}

.profile-status-card {
  position: relative;
  display: grid;
  grid-template-columns: 82px minmax(0, 1fr);
  align-items: center;
  gap: 12px;
  min-height: 94px;
  padding: 12px 18px;
}

.status-icon {
  display: grid;
  place-items: center;
  width: 82px;
  height: 82px;
  overflow: hidden;
  border: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
}

.profile-status-card b,
.profile-status-card strong {
  display: block;
}

.profile-status-card b {
  color: #0b2b6f;
  font-size: 15px;
}

.profile-status-card strong {
  margin-top: 4px;
  color: #5c7392;
  font-size: 12px;
}

.profile-status-card.done .status-check {
  background: linear-gradient(135deg, #10b981, #00c8f5);
}

.status-check {
  position: absolute;
  top: 12px;
  right: 12px;
  display: grid;
  place-items: center;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #b9c8db;
  color: #fff;
  font-size: 11px;
  font-weight: 950;
}

.profile-info-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
}

.profile-section-card {
  overflow: hidden;
  background:
    radial-gradient(circle at 10% 0%, rgba(0, 200, 245, 0.12), transparent 30%),
    rgba(255, 255, 255, 0.72);
}

.section-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 16px;
}

.section-head h3,
.experience-head h3 {
  margin: 7px 0 0;
  color: #071a3d;
  font-size: 20px;
  line-height: 1.25;
}

.profile-secondary-btn {
  border: 1px solid rgba(69, 145, 255, 0.28);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.56);
  color: #1e63c7;
  font-weight: 850;
}

.profile-page :deep(.el-form-item__label) {
  color: #536b8e;
  font-weight: 850;
}

.profile-page :deep(.el-input__wrapper),
.profile-page :deep(.el-select__wrapper),
.profile-page :deep(.el-cascader .el-input__wrapper),
.profile-page :deep(.el-textarea__inner) {
  min-height: 38px;
  border: 1px solid rgba(69, 145, 255, 0.28);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.72);
  box-shadow: none;
  transition: border-color 180ms ease, box-shadow 180ms ease, background 180ms ease;
}

.profile-page :deep(.el-input__wrapper.is-focus),
.profile-page :deep(.el-select__wrapper.is-focused),
.profile-page :deep(.el-textarea__inner:focus) {
  border-color: rgba(30, 123, 255, 0.68);
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 0 0 4px rgba(30, 123, 255, 0.1);
}

.profile-page :deep(.el-select),
.profile-page :deep(.el-cascader),
.profile-page :deep(.el-autocomplete) {
  width: 100%;
}

.school-field {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.school-badges {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-width: 184px;
}

.elite-badge {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 52px;
  height: 25px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.72);
  border-radius: 999px;
  color: #fff;
  font-size: 12px;
  font-weight: 950;
  line-height: 1;
  text-align: center;
  text-shadow: 0 1px 8px rgba(4, 25, 68, 0.34);
  box-shadow: 0 8px 18px rgba(30, 123, 255, 0.2);
  transform-style: preserve-3d;
  animation: badgeFlip 3.4s ease-in-out infinite;
}

.elite-badge::before {
  position: absolute;
  inset: 1px 4px auto;
  height: 45%;
  content: "";
  border-radius: 999px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.48), transparent);
  opacity: 0.78;
  pointer-events: none;
}

.elite-badge-985 {
  background: linear-gradient(135deg, #ff8a00 0%, #ffd166 48%, #2f86ff 100%);
  animation-delay: 0s;
}

.elite-badge-211 {
  background: linear-gradient(135deg, #1e7bff 0%, #00c8f5 100%);
  animation-delay: 0.18s;
}

.elite-badge-double {
  min-width: 70px;
  background: linear-gradient(135deg, #6d5dfc 0%, #1e7bff 54%, #00c8f5 100%);
  animation-delay: 0.36s;
}

.salary-range {
  display: grid;
  grid-template-columns: minmax(96px, 1fr) auto minmax(96px, 1fr) auto;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.salary-range span,
.salary-range em,
.select-meta {
  color: #647895;
  font-style: normal;
  font-size: 12px;
}

.select-meta {
  margin-top: 8px;
  line-height: 1.5;
}

.chip-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.profile-chip {
  display: inline-flex;
  align-items: center;
  min-height: 26px;
  border: 1px solid rgba(95, 159, 255, 0.35);
  border-radius: 999px;
  padding: 4px 10px;
  background: rgba(235, 243, 255, 0.9);
  color: #42618a;
  font-size: 12px;
  font-weight: 850;
}

.certificate-chip {
  background: rgba(232, 248, 255, 0.88);
}

.more-chip {
  color: #1e63c7;
}

.profile-experience-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
}

.experience-card {
  display: flex;
  min-height: 332px;
  flex-direction: column;
  padding: 20px;
}

.experience-head {
  display: grid;
  grid-template-columns: 92px minmax(0, 1fr) auto;
  align-items: center;
  gap: 16px;
  margin-bottom: 18px;
}

.experience-icon {
  display: grid;
  place-items: center;
  width: 92px;
  height: 92px;
  overflow: hidden;
  border: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
}

.experience-head p {
  margin: 7px 0 0;
  color: #647895;
  font-size: 12px;
  font-weight: 750;
  line-height: 1.6;
}

.experience-head b {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 52px;
  height: 32px;
  border: 1px solid rgba(255, 255, 255, 0.88);
  border-radius: 999px;
  padding: 0 12px;
  background: linear-gradient(135deg, rgba(30, 123, 255, 0.92), rgba(0, 200, 245, 0.82));
  box-shadow: 0 12px 24px rgba(30, 123, 255, 0.18);
  color: #fff;
  font-size: 13px;
  white-space: nowrap;
}

.tag-editor {
  display: flex;
  flex: 1;
  min-height: 160px;
  flex-direction: column;
  gap: 14px;
}

.experience-list {
  display: grid;
  gap: 10px;
  max-height: 150px;
  overflow-y: auto;
  padding-right: 3px;
}

.experience-list::-webkit-scrollbar {
  width: 4px;
}

.experience-list::-webkit-scrollbar-thumb {
  border-radius: 99px;
  background: rgba(30, 123, 255, 0.24);
}

.experience-item {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 10px;
  border: 1px solid rgba(190, 213, 242, 0.76);
  border-radius: 16px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.62);
  transition: border-color 180ms ease, box-shadow 180ms ease, transform 180ms ease;
}

.experience-item:hover {
  border-color: rgba(0, 200, 245, 0.42);
  box-shadow: 0 14px 34px rgba(30, 123, 255, 0.1);
  transform: translateY(-1px);
}

.experience-index {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border-radius: 12px;
  background: rgba(30, 123, 255, 0.1);
  color: #1455b8;
  font-size: 12px;
  font-weight: 950;
}

.experience-item p {
  overflow: hidden;
  margin: 0;
  color: #14346c;
  font-size: 13px;
  font-weight: 800;
  line-height: 1.55;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.experience-empty {
  display: flex;
  align-items: center;
  gap: 11px;
  min-height: 92px;
  border: 1px dashed rgba(30, 123, 255, 0.25);
  border-radius: 18px;
  padding: 14px;
  background:
    radial-gradient(circle at 50% 0%, rgba(0, 200, 245, 0.1), transparent 42%),
    rgba(255, 255, 255, 0.48);
  text-align: left;
}

.experience-empty span {
  flex: 0 0 auto;
  width: 36px;
  height: 36px;
  border-radius: 13px;
  background: linear-gradient(90deg, #1e7bff, #00c8f5);
  box-shadow: 0 0 16px rgba(0, 200, 245, 0.34);
}

.experience-empty p {
  min-width: 0;
  margin: 0;
  color: #647895;
  font-size: 13px;
  font-weight: 750;
  line-height: 1.65;
}

.tag-input-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 96px;
  align-items: center;
  gap: 16px;
  margin-top: auto;
  border-top: 1px solid rgba(147, 197, 253, 0.2);
  padding-top: 16px;
}

.tag-input-row :deep(.el-button) {
  width: 96px;
  min-height: 40px;
  border-radius: 15px;
}

@keyframes badgeFlip {
  0%,
  72%,
  100% {
    transform: perspective(240px) rotateY(0deg) translateY(0);
  }

  80% {
    transform: perspective(240px) rotateY(18deg) translateY(-1px);
  }

  88% {
    transform: perspective(240px) rotateY(-16deg) translateY(0);
  }

  94% {
    transform: perspective(240px) rotateY(8deg) translateY(-1px);
  }
}

@keyframes flowDashedOrbit {
  to {
    transform: rotate(360deg);
  }
}

@keyframes flowAuroraTravel {
  to {
    stroke-dashoffset: -18;
  }
}

.profile-card-side {
  display: grid;
  flex: 0 0 auto;
  place-items: center;
  gap: 12px;
}

.profile-card-side .profile-save-btn {
  min-width: 132px;
}

@media (max-width: 1380px) {
  .profile-flow {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .profile-flow-summary {
    grid-column: span 3;
  }

  .profile-status-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 1024px) {
  .profile-card {
    align-items: flex-start;
    flex-direction: column;
  }

  .profile-card-side,
  .completion-panel {
    justify-self: center;
    width: 100%;
  }

  .profile-info-grid,
  .profile-experience-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .profile-page {
    gap: 16px;
  }

  .profile-identity,
  .identity-targets {
    align-items: flex-start;
    flex-direction: column;
  }

  .profile-flow,
  .profile-status-grid {
    grid-template-columns: 1fr;
  }

  .profile-flow-summary {
    grid-column: auto;
  }

  .school-field,
  .salary-range,
  .tag-input-row {
    grid-template-columns: 1fr;
  }

  .school-badges {
    min-width: 0;
  }

  .tag-input-row :deep(.el-button) {
    width: 100%;
  }
}
</style>
