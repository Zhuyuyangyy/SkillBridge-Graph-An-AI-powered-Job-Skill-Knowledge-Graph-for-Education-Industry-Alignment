<template>
  <el-container class="app-shell">
    <el-aside class="app-aside" width="266px">
      <div class="aside-glow"></div>
      <div class="brand">
        <div class="brand-mark">
          <span>SR</span>
        </div>
        <div class="brand-copy">
          <div class="brand-name">数融智联</div>
          <div class="brand-desc">岗位能力图谱分析系统</div>
        </div>
      </div>

      <div class="status-card">
        <span class="status-sprite-shell">
          <IconSprite name="shield" :size="38" />
        </span>
        <div>
          <b>能力网络在线</b>
          <span>智能服务 · 证据校验</span>
        </div>
        <el-icon class="status-arrow"><ArrowRight /></el-icon>
      </div>

      <el-menu :default-active="activeMenu" class="side-menu" @select="handleMenuSelect">
        <el-menu-item v-for="item in visibleMenus" :key="item.path" :index="item.path">
          <span class="active-rail"></span>
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
          <el-icon class="menu-arrow"><ArrowRight /></el-icon>
        </el-menu-item>
      </el-menu>

      <div class="aside-deco">
        <div class="aside-deco-orbit"></div>
        <IconSprite name="profile" :size="146" />
      </div>
    </el-aside>

    <el-container>
      <el-header class="app-header">
        <div class="header-main">
          <div class="header-title-row">
            <span class="section-mark"></span>
            <div class="header-title">{{ $route.meta.title }}</div>
          </div>
          <div class="header-desc">{{ headerSubtitle }}</div>
        </div>
        <div class="header-actions">
          <div class="search-bar-shell">
            <span class="search-glow"></span>
            <span class="search-white"></span>
            <span class="search-border"></span>
            <span class="search-dark-border"></span>
            <el-autocomplete
              v-model="searchKeyword"
              class="global-search"
              value-key="label"
              clearable
              :fetch-suggestions="querySearch"
              placeholder="搜索页面、岗位、简历或能力"
              @select="handleSearchSelect"
              @keydown.enter="handleSearchEnter"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
              <template #default="{ item }">
                <div class="search-suggestion">
                  <span>{{ item.label }}</span>
                  <small>{{ item.hint }}</small>
                </div>
              </template>
            </el-autocomplete>
          </div>
          <button class="theme-switch" type="button" :class="{ dark: isDarkTheme }" :aria-label="isDarkTheme ? '切换白天模式' : '切换黑夜模式'" @click="toggleTheme">
            <span class="theme-slider">
              <span class="theme-sun-moon">
                <i class="moon-dot dot-1"></i>
                <i class="moon-dot dot-2"></i>
                <i class="moon-dot dot-3"></i>
                <i class="light-ray ray-1"></i>
                <i class="light-ray ray-2"></i>
                <i class="light-ray ray-3"></i>
              </span>
              <i class="theme-cloud cloud-1"></i>
              <i class="theme-cloud cloud-2"></i>
              <i class="theme-cloud cloud-3"></i>
              <i class="theme-star star-1"></i>
              <i class="theme-star star-2"></i>
              <i class="theme-star star-3"></i>
            </span>
          </button>
          <el-tag effect="light" type="success">SQLite 已连接</el-tag>
          <el-tag effect="light" type="primary">{{ roleLabel }}</el-tag>
            <el-dropdown trigger="click" @command="handleUserCommand">
            <button class="user-chip">
              <el-avatar class="user-avatar" :size="34" :src="userAvatar || undefined">{{ userAvatar ? '' : userInitial }}</el-avatar>
              <span>{{ auth.user?.display_name || auth.user?.username }}</span>
            </button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="account">账号设置</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="app-main">
        <RouterView />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import {
  Aim,
  ArrowRight,
  ChatDotRound,
  Connection,
  DataAnalysis,
  DataLine,
  Document,
  Files,
  Histogram,
  List,
  Management,
  Operation,
  Reading,
  Search,
  Setting,
  Share,
  TrendCharts,
  User,
  VideoCamera
} from '@element-plus/icons-vue'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import IconSprite from '@/components/IconSprite.vue'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/api/http'

const menus = [
  { path: '/overview', label: '系统概览', icon: Histogram, roles: ['candidate', 'hr', 'admin'] },
  { path: '/personal-center', label: '个人中心', icon: User, roles: ['candidate'] },
  { path: '/hr-candidates', label: '候选人管理', icon: User, roles: ['hr', 'admin'] },
  { path: '/datasets', label: '数据源管理', icon: Files, roles: ['hr', 'admin'] },
  { path: '/jd-parser', label: 'JD解析', icon: Document, roles: ['hr', 'admin'] },
  { path: '/jobs', label: '岗位管理', icon: Management, roles: ['hr', 'admin'] },
  { path: '/emerging-jobs', label: '新岗位发现', icon: TrendCharts, roles: ['hr', 'admin'] },
  { path: '/job-evolution', label: '岗位能力更新', icon: Operation, roles: ['hr', 'admin'] },
  { path: '/skill-graph', label: '能力图谱', icon: Connection, roles: ['candidate', 'hr', 'admin'] },
  { path: '/graph-explore', label: '图谱探索', icon: Share, roles: ['candidate', 'hr', 'admin'] },
  { path: '/capability-evolution', label: '能力演化', icon: DataLine, roles: ['candidate', 'hr', 'admin'] },
  { path: '/resume-parser', label: '简历解析', icon: User, roles: ['candidate', 'hr', 'admin'] },
  { path: '/match-analysis', label: '匹配分析', icon: Aim, roles: ['candidate', 'hr', 'admin'] },
  { path: '/digital-interviewer', label: '数字人面试官', icon: VideoCamera, roles: ['candidate', 'hr', 'admin'] },
  { path: '/learning-path', label: '学习路径', icon: Reading, roles: ['candidate'] },
  { path: '/review-tasks', label: '人工审核', icon: List, roles: ['hr', 'admin'] },
  { path: '/evaluation', label: '测试评估', icon: DataAnalysis, roles: ['hr', 'admin'] },
  { path: '/settings', label: '系统设置', icon: Setting, roles: ['hr', 'admin'] },
  { path: '/account-settings', label: '账号设置', icon: Setting, roles: ['candidate', 'hr', 'admin'] }
]

void ChatDotRound

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const searchKeyword = ref('')
const candidateAvatar = ref('')
const isDarkTheme = ref(localStorage.getItem('sr-theme') === 'dark')
const visibleMenus = computed(() => menus.filter((item) => item.roles.includes(auth.role || 'candidate')))
const activeMenu = computed(() => route.path)
const roleLabel = computed(() => (auth.role === 'hr' ? '企业 HR' : auth.role === 'admin' ? '管理员' : '求职者/学生'))
const userInitial = computed(() => (auth.user?.display_name || auth.user?.username || '用').slice(0, 1))
const userAvatar = computed(() => (auth.role === 'candidate' ? candidateAvatar.value : ''))
const headerSubtitle = computed(() => {
  const map: Record<string, string> = {
    '/overview': '查看岗位数据、能力图谱、解析质量和系统运行概况',
    '/personal-center': '维护个人画像，查看匹配分析、学习路径和面试练习',
    '/hr-candidates': '查看求职者提交的个人画像、简历、技能证书和匹配准备情况',
    '/datasets': '管理多源 JD 数据，观察质量评分、重复率、噪声率和处理状态',
    '/jd-parser': '输入岗位 JD 文本，提取岗位名称、职责、技能、工具、证书、场景和证据来源',
    '/jobs': '按领域、类型和等级筛选岗位，查看岗位画像、状态、版本和证据来源',
    '/emerging-jobs': '基于多源一致性、技能增长和场景扩散识别新岗位候选',
    '/job-evolution': '选择岗位后查看新增、删除、修改技能和版本记录',
    '/skill-graph': '展示岗位、技能、工具、证书、课程和等级之间的关系',
    '/graph-explore': '社区聚类、核心枢纽识别与岗位间技能迁移路径分析',
    '/capability-evolution': '追踪岗位能力的新增、淘汰、迁移趋势与领域能力结构对比',
    '/resume-parser': '整理教育经历、项目经历、技能、证书、竞赛经历和岗位意向',
    '/match-analysis': '选择简历与目标岗位，查看匹配结论、能力差距、风险提醒和下一步行动',
    '/digital-interviewer': '围绕目标岗位进行结构化追问、表达反馈和能力评分',
    '/learning-path': '基于最近一次人岗匹配差距，生成阶段化成长路线',
    '/review-tasks': '处理低置信度的新岗位、新技能、删除技能和修改技能任务',
    '/evaluation': '查看 JD 解析、简历解析、匹配分析、测试用例数量和单元测试评估结果',
    '/settings': '管理智能服务配置、图谱写入规则和审核阈值',
    '/account-settings': '维护账号资料、联系方式和登录密码'
  }
  return map[route.path] || (auth.role === 'candidate' ? '维护个人画像，查看岗位匹配和学习路径' : '管理岗位数据、能力图谱和候选人资料')
})
const searchTargets = computed(() =>
  visibleMenus.value.map((item) => ({
    label: item.label,
    path: item.path,
    hint: routeHint(item.path),
    keywords: `${item.label} ${routeHint(item.path)} ${routeAliases(item.path)}`
  }))
)

onMounted(() => {
  applyThemeClass()
  loadCandidateAvatar()
  window.addEventListener('profile-avatar-updated', handleAvatarUpdated as EventListener)
})

onBeforeUnmount(() => {
  window.removeEventListener('profile-avatar-updated', handleAvatarUpdated as EventListener)
})

function handleMenuSelect(path: string) {
  if (path === route.path) return
  router.push(path).catch(() => undefined)
}

function querySearch(query: string, callback: (items: any[]) => void) {
  const keyword = query.trim().toLowerCase()
  const rows = searchTargets.value.filter((item) => !keyword || item.keywords.toLowerCase().includes(keyword))
  callback(rows.slice(0, 8))
}

function handleSearchSelect(item: { path: string }) {
  searchKeyword.value = ''
  router.push(item.path).catch(() => undefined)
}

function handleSearchEnter() {
  const keyword = searchKeyword.value.trim().toLowerCase()
  if (!keyword) return
  const match = searchTargets.value.find((item) => item.keywords.toLowerCase().includes(keyword))
  if (!match) {
    ElMessage.info('没有找到匹配的功能入口')
    return
  }
  handleSearchSelect(match)
}

async function loadCandidateAvatar() {
  if (auth.role !== 'candidate' || !auth.token) return
  try {
    const profile = await api.myProfile()
    candidateAvatar.value = profile.avatar_url || ''
  } catch {
    candidateAvatar.value = ''
  }
}

function handleAvatarUpdated(event: CustomEvent<{ avatar_url?: string }>) {
  candidateAvatar.value = event.detail?.avatar_url || ''
}

function toggleTheme() {
  isDarkTheme.value = !isDarkTheme.value
  localStorage.setItem('sr-theme', isDarkTheme.value ? 'dark' : 'light')
  applyThemeClass()
}

function applyThemeClass() {
  document.body.classList.toggle('theme-dark', isDarkTheme.value)
}

function routeHint(path: string) {
  const map: Record<string, string> = {
    '/overview': '指标概览',
    '/personal-center': '头像 画像 能力 证书',
    '/hr-candidates': '候选人 简历 画像',
    '/datasets': '数据源 上传 质量',
    '/jd-parser': 'JD 解析 岗位抽取',
    '/jobs': '岗位 管理 描述',
    '/emerging-jobs': '新岗位 发现',
    '/job-evolution': '能力更新 版本',
    '/skill-graph': '能力图谱 关系',
    '/graph-explore': '图谱探索 社区 枢纽 迁移路径',
    '/capability-evolution': '能力演化 趋势 热点 淘汰 对比',
    '/resume-parser': '简历解析',
    '/match-analysis': '人岗匹配 分析',
    '/digital-interviewer': '数字人 面试',
    '/learning-path': '学习路径 推荐',
    '/review-tasks': '人工审核',
    '/evaluation': '测试评估',
    '/settings': '系统设置',
    '/account-settings': '账号 密码 邮箱'
  }
  return map[path] || '功能入口'
}

function routeAliases(path: string) {
  const map: Record<string, string> = {
    '/jobs': '工程师 架构师 分析师 顾问 岗位库',
    '/skill-graph': '技能 工具 证书 课程',
    '/resume-parser': '上传简历 文本简历',
    '/match-analysis': '匹配度 缺失技能 建议',
    '/personal-center': '个人中心 自定义头像 个人资料',
    '/hr-candidates': '求职者 学生 HR 后台',
    '/digital-interviewer': '在线面试官 数字人'
  }
  return map[path] || ''
}

async function handleUserCommand(command: string) {
  if (command === 'account') {
    router.push('/account-settings').catch(() => undefined)
  }
  if (command === 'logout') {
    await auth.logout()
    router.push('/login').catch(() => undefined)
  }
}
</script>

<style scoped>
@property --search-border-angle {
  syntax: "<angle>";
  inherits: false;
  initial-value: 0deg;
}

.app-shell {
  min-height: 100vh;
  color: var(--text);
}

.app-aside {
  position: sticky;
  top: 0;
  z-index: 20;
  height: 100vh;
  overflow: hidden;
  border-right: 1px solid rgba(190, 213, 242, 0.82);
  background:
    linear-gradient(180deg, rgba(248, 251, 255, 0.96), rgba(229, 241, 255, 0.92) 46%, rgba(218, 235, 255, 0.84)),
    rgba(255, 255, 255, 0.86);
  box-shadow: 16px 0 54px rgba(37, 99, 235, 0.12);
  backdrop-filter: blur(24px);
}

.aside-glow {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.aside-glow::before {
  position: absolute;
  left: 26px;
  top: 90px;
  width: 160px;
  height: 340px;
  content: "";
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.11);
  filter: blur(52px);
  transform: rotate(12deg);
}

.aside-glow::after {
  position: absolute;
  inset-block: 0;
  right: 0;
  width: 1px;
  content: "";
  background: linear-gradient(180deg, transparent, rgba(255, 255, 255, 0.95), transparent);
}

.brand {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 88px;
  padding: 20px 18px 16px;
  border-bottom: 1px solid rgba(190, 213, 242, 0.68);
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 52px;
  height: 52px;
  border: 1px solid rgba(255, 255, 255, 0.9);
  border-radius: 18px;
  background:
    radial-gradient(circle at 30% 20%, rgba(255, 255, 255, 0.92), transparent 28%),
    linear-gradient(135deg, #2563eb, #06b6d4);
  box-shadow: 0 0 30px rgba(6, 182, 212, 0.28);
  color: #fff;
  font-size: 18px;
  font-weight: 950;
}

.brand-copy {
  min-width: 0;
}

.brand-name {
  color: #071a3d;
  font-size: 20px;
  font-weight: 950;
}

.brand-desc {
  margin-top: 6px;
  color: #53657e;
  font-size: 12px;
  font-weight: 800;
}

.status-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 14px 14px 12px;
  border: 1px solid rgba(190, 213, 242, 0.82);
  border-radius: 18px;
  padding: 12px;
  background:
    radial-gradient(circle at 12% 0%, rgba(6, 182, 212, 0.12), transparent 30%),
    rgba(255, 255, 255, 0.64);
  box-shadow: 0 10px 30px rgba(37, 99, 235, 0.08);
  animation: sideCardPulse 6.2s ease-in-out infinite;
}

.status-sprite-shell {
  display: grid;
  flex: 0 0 auto;
  place-items: center;
  width: 46px;
  height: 46px;
  overflow: hidden;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.1), rgba(6, 182, 212, 0.12));
}

.status-card b {
  display: block;
  color: #14346c;
  font-size: 13px;
}

.status-card > div span {
  display: block;
  margin-top: 4px;
  color: var(--muted);
  font-size: 11px;
  font-weight: 700;
}

.status-arrow {
  margin-left: auto;
  color: #2563eb;
}

.side-menu {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: calc(100vh - 132px);
  overflow-y: auto;
  padding: 0 12px;
  border: 0;
  background: transparent;
}

.side-menu::-webkit-scrollbar {
  width: 4px;
}

.side-menu::-webkit-scrollbar-thumb {
  border-radius: 99px;
  background: rgba(37, 99, 235, 0.22);
}

:deep(.el-menu-item) {
  position: relative;
  height: 39px;
  overflow: hidden;
  border: 1px solid transparent;
  border-radius: 15px;
  color: #52647d;
  font-weight: 850;
  transition: all 220ms ease;
}

:deep(.el-menu-item .el-icon:first-of-type) {
  transition: transform 220ms ease, color 220ms ease, filter 220ms ease;
}

:deep(.el-menu-item::after) {
  position: absolute;
  top: 0;
  left: -80%;
  width: 58%;
  height: 100%;
  content: "";
  background: linear-gradient(100deg, transparent, rgba(255, 255, 255, 0.66), transparent);
  transform: skewX(-18deg);
  transition: left 620ms ease;
}

:deep(.el-menu-item:hover::after) {
  left: 130%;
}

:deep(.el-menu-item:hover) {
  border-color: rgba(190, 213, 242, 0.86);
  background: rgba(255, 255, 255, 0.58);
  color: #1455b8;
  transform: translateX(3px);
}

:deep(.el-menu-item:hover .el-icon:first-of-type),
:deep(.el-menu-item.is-active .el-icon:first-of-type) {
  filter: drop-shadow(0 0 8px rgba(6, 182, 212, 0.32));
  transform: scale(1.08);
}

:deep(.el-menu-item.is-active) {
  border-color: rgba(37, 99, 235, 0.24);
  background: rgba(37, 99, 235, 0.1);
  color: #1455b8;
  box-shadow: 0 14px 34px rgba(37, 99, 235, 0.14);
}

:deep(.el-menu-item.is-active)::before {
  position: absolute;
  top: 50%;
  right: 12px;
  width: 7px;
  height: 7px;
  content: "";
  border-radius: 50%;
  background: linear-gradient(180deg, var(--primary), var(--cyan));
  box-shadow: 0 0 14px rgba(6, 182, 212, 0.72);
  transform: translateY(-50%);
}

.active-rail {
  position: absolute;
  left: 0;
  top: 50%;
  display: none;
  width: 4px;
  height: 28px;
  border-radius: 0 99px 99px 0;
  background: linear-gradient(180deg, var(--primary), var(--cyan));
  box-shadow: 0 0 16px rgba(6, 182, 212, 0.8);
  transform: translateY(-50%);
}

:deep(.el-menu-item.is-active) .active-rail {
  display: block;
}

.menu-arrow {
  margin-left: auto;
  opacity: 0;
  transition: opacity 200ms ease, transform 200ms ease;
}

:deep(.el-menu-item.is-active) .menu-arrow,
:deep(.el-menu-item:hover) .menu-arrow {
  opacity: 1;
  transform: translateX(2px);
}

.aside-deco {
  display: none;
  position: absolute;
  right: 18px;
  bottom: 20px;
  left: 18px;
  display: grid;
  place-items: center;
  height: 132px;
  overflow: hidden;
  border: 1px solid rgba(104, 211, 255, 0.2);
  border-radius: 24px;
  background:
    radial-gradient(circle at 50% 45%, rgba(0, 200, 245, 0.14), transparent 42%),
    rgba(255, 255, 255, 0.08);
  pointer-events: none;
}

.aside-deco-orbit {
  position: absolute;
  width: 112px;
  height: 112px;
  border: 1px dashed rgba(104, 211, 255, 0.38);
  border-radius: 50%;
  animation: asideOrbit 12s linear infinite;
}

.aside-deco :deep(.sprite-icon) {
  opacity: 0.5;
  transform: translateY(18px);
}

.app-header {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 94px;
  overflow: hidden;
  border-bottom: 1px solid rgba(107, 174, 255, 0.28);
  background:
    radial-gradient(circle at 20% 0%, rgba(0, 200, 245, 0.14), transparent 28%),
    radial-gradient(circle at 82% 18%, rgba(30, 123, 255, 0.12), transparent 28%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.86), rgba(232, 245, 255, 0.74));
  box-shadow: 0 12px 34px rgba(37, 99, 235, 0.08);
  backdrop-filter: blur(18px);
}

.app-header::after {
  position: absolute;
  left: 24px;
  bottom: 0;
  width: 176px;
  height: 3px;
  content: "";
  border-radius: 99px;
  background: linear-gradient(90deg, #1e7bff, #00c8f5);
  box-shadow: 0 0 18px rgba(0, 200, 245, 0.42);
  animation: headerLineBreath 4.8s ease-in-out infinite;
}

.header-main {
  min-width: 0;
  padding-left: 2px;
}

.header-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.section-mark {
  width: 4px;
  height: 28px;
  border-radius: 99px;
  background: linear-gradient(180deg, #2563eb, #06b6d4);
  box-shadow: 0 0 18px rgba(6, 182, 212, 0.34);
}

.header-title {
  color: #071a3d;
  font-size: 25px;
  font-weight: 950;
  line-height: 1.2;
}

.header-desc {
  margin-top: 7px;
  color: #526b8e;
  font-size: 14px;
  font-weight: 750;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 0 0 auto;
}

.search-bar-shell {
  --search-border-angle: 0deg;

  position: relative;
  z-index: 1;
  display: grid;
  place-items: center;
  width: 326px;
  height: 48px;
  isolation: isolate;
  overflow: hidden;
  border-radius: 16px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.92), rgba(239, 248, 255, 0.78));
  box-shadow: 0 10px 26px rgba(37, 99, 235, 0.08);
}

.search-glow,
.search-white,
.search-border,
.search-dark-border {
  display: none;
}

.search-bar-shell::before {
  position: absolute;
  z-index: 0;
  inset: 0;
  content: "";
  padding: 2px;
  border-radius: inherit;
  background:
    conic-gradient(
      from var(--search-border-angle),
      transparent 0deg,
      transparent 26deg,
      rgba(0, 200, 245, 0.12) 35deg,
      rgba(77, 245, 255, 0.62) 44deg,
      rgba(255, 255, 255, 0.88) 50deg,
      rgba(30, 123, 255, 0.54) 58deg,
      transparent 72deg,
      transparent 190deg,
      rgba(77, 245, 255, 0.5) 208deg,
      rgba(255, 255, 255, 0.76) 216deg,
      rgba(30, 123, 255, 0.5) 226deg,
      transparent 244deg,
      transparent 360deg
    );
  opacity: 0.64;
  -webkit-mask:
    linear-gradient(#000 0 0) content-box,
    linear-gradient(#000 0 0);
  -webkit-mask-composite: xor;
  mask:
    linear-gradient(#000 0 0) content-box,
    linear-gradient(#000 0 0);
  mask-composite: exclude;
  pointer-events: none;
  animation: searchBorderSpin 9s linear infinite;
}

.search-bar-shell:focus-within::before,
.search-bar-shell:hover::before {
  opacity: 0.82;
}

.global-search {
  width: 316px;
  position: relative;
  z-index: 1;
}

.global-search :deep(.el-input__wrapper) {
  height: 42px;
  border: 1px solid rgba(190, 213, 242, 0.24);
  border-radius: 13px;
  background: transparent;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.92),
    0 8px 24px rgba(37, 99, 235, 0.04);
  transition: border-color 180ms ease, box-shadow 180ms ease, background 180ms ease;
}

.global-search :deep(.el-input__wrapper.is-focus) {
  border-color: rgba(0, 200, 245, 0.58);
  box-shadow:
    0 0 0 3px rgba(0, 200, 245, 0.08),
    0 12px 30px rgba(37, 99, 235, 0.14);
}

.global-search :deep(.el-input__prefix) {
  color: var(--primary);
}

.theme-switch {
  position: relative;
  flex: 0 0 auto;
  width: 60px;
  height: 34px;
  border: 0;
  padding: 0;
  background: transparent;
  cursor: pointer;
}

.theme-slider {
  position: absolute;
  inset: 0;
  overflow: hidden;
  border: 1px solid rgba(93, 168, 255, 0.56);
  border-radius: 34px;
  background: linear-gradient(135deg, #51b6ff, #2196f3);
  box-shadow: 0 10px 22px rgba(33, 150, 243, 0.2);
  transition: background 0.4s ease, box-shadow 0.4s ease;
}

.theme-switch.dark .theme-slider {
  border-color: rgba(88, 112, 180, 0.62);
  background: linear-gradient(135deg, #071124, #101b3d);
  box-shadow: 0 10px 24px rgba(5, 10, 25, 0.24);
}

.theme-sun-moon {
  position: absolute;
  z-index: 3;
  left: 4px;
  bottom: 4px;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: #ffe45c;
  box-shadow: 0 0 16px rgba(255, 228, 92, 0.55);
  transition: transform 0.4s ease, background 0.4s ease, box-shadow 0.4s ease;
}

.theme-switch.dark .theme-sun-moon {
  transform: translateX(26px) rotate(180deg);
  background: #fff;
  box-shadow: 0 0 14px rgba(255, 255, 255, 0.48);
}

.moon-dot,
.light-ray,
.theme-cloud,
.theme-star {
  position: absolute;
  display: block;
  pointer-events: none;
}

.moon-dot {
  border-radius: 50%;
  background: #9ca3af;
  opacity: 0;
  transition: opacity 0.35s ease;
}

.theme-switch.dark .moon-dot {
  opacity: 1;
}

.dot-1 {
  top: 4px;
  left: 11px;
  width: 6px;
  height: 6px;
}

.dot-2 {
  top: 11px;
  left: 3px;
  width: 9px;
  height: 9px;
}

.dot-3 {
  top: 19px;
  left: 17px;
  width: 3px;
  height: 3px;
}

.light-ray {
  z-index: -1;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.ray-1 {
  inset: -8px;
}

.ray-2 {
  inset: -14px;
}

.ray-3 {
  inset: -20px;
}

.theme-cloud {
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.74);
  animation: themeCloudMove 6s ease-in-out infinite;
}

.cloud-1 {
  right: -3px;
  top: 15px;
  width: 34px;
  height: 9px;
}

.cloud-2 {
  right: 6px;
  top: 10px;
  width: 18px;
  height: 7px;
  animation-delay: 0.8s;
}

.cloud-3 {
  right: 18px;
  top: 24px;
  width: 26px;
  height: 8px;
  animation-delay: 1.3s;
}

.theme-switch.dark .theme-cloud {
  opacity: 0;
}

.theme-star {
  border-radius: 50%;
  background: #fff;
  opacity: 0;
  transform: translateY(-20px);
  transition: opacity 0.35s ease, transform 0.35s ease;
  animation: themeStarTwinkle 2s ease-in-out infinite;
}

.theme-switch.dark .theme-star {
  opacity: 1;
  transform: translateY(0);
}

.star-1 {
  left: 8px;
  top: 8px;
  width: 5px;
  height: 5px;
}

.star-2 {
  left: 18px;
  top: 20px;
  width: 3px;
  height: 3px;
  animation-delay: 0.5s;
}

.star-3 {
  left: 29px;
  top: 7px;
  width: 4px;
  height: 4px;
  animation-delay: 1.1s;
}

.search-suggestion {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  width: 100%;
}

.search-suggestion span {
  color: #0f2b57;
  font-weight: 850;
}

.search-suggestion small {
  overflow: hidden;
  max-width: 150px;
  color: #8a9bb1;
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-avatar {
  background: linear-gradient(135deg, var(--primary), var(--cyan));
  box-shadow: 0 10px 22px rgba(37, 99, 235, 0.25);
  font-weight: 950;
}

.user-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  max-width: 176px;
  border: 1px solid rgba(190, 213, 242, 0.88);
  border-radius: 16px;
  padding: 5px 10px 5px 5px;
  background: rgba(255, 255, 255, 0.74);
  color: #14346c;
  font-weight: 850;
}

.user-chip span {
  overflow: hidden;
  min-width: 0;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.app-main {
  padding: 18px 22px 28px;
}

@keyframes asideOrbit {
  to {
    transform: rotate(360deg);
  }
}

@keyframes headerLineBreath {
  0%,
  100% {
    opacity: 0.72;
    width: 176px;
  }

  50% {
    opacity: 1;
    width: 236px;
  }
}

@keyframes searchAuraSpin {
  to {
    transform: translate(-50%, -50%) rotate(436deg);
  }
}

@keyframes searchBorderSpin {
  to {
    --search-border-angle: 360deg;
  }
}

@keyframes themeCloudMove {
  0%,
  100% {
    transform: translateX(0);
  }

  45% {
    transform: translateX(4px);
  }

  80% {
    transform: translateX(-4px);
  }
}

@keyframes themeStarTwinkle {
  0%,
  100% {
    transform: scale(1);
  }

  45% {
    transform: scale(1.28);
  }

  80% {
    transform: scale(0.82);
  }
}

@keyframes sideCardPulse {
  0%,
  100% {
    box-shadow: 0 10px 30px rgba(37, 99, 235, 0.08);
  }

  50% {
    box-shadow: 0 16px 36px rgba(6, 182, 212, 0.14);
  }
}
</style>
