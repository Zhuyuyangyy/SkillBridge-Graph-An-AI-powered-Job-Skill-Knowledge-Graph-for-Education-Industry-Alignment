<template>
  <div class="login-page" @pointermove="handlePointerMove" @pointerleave="resetTilt">
    <div class="aurora aurora-a"></div>
    <div class="aurora aurora-b"></div>
    <div class="scan-line"></div>
    <div class="matrix-grid"></div>
    <div class="particle-field">
      <i v-for="item in 54" :key="item" :style="particleStyle(item)"></i>
    </div>

    <main class="login-stage">
      <div class="orbit-shell" aria-hidden="true">
        <span class="orbit-ring ring-outer"></span>
        <span class="orbit-ring ring-middle"></span>
        <span class="orbit-ring ring-dashed"></span>
        <span class="orbit-ring ring-inner"></span>
        <span class="orbit-runner runner-a"><i></i></span>
        <span class="orbit-runner runner-b"><i></i></span>
        <span class="orbit-runner runner-c"><i></i></span>
        <span class="orbit-dot dot-a"></span>
        <span class="orbit-dot dot-b"></span>
        <span class="orbit-dot dot-c"></span>
        <span class="orbit-cross cross-a"></span>
        <span class="orbit-cross cross-b"></span>
      </div>

      <section class="auth-card" :class="{ 'auth-register': mode === 'register', 'auth-login': mode === 'login' }" :style="cardTiltStyle">
        <div class="tech-decoration" aria-hidden="true">
          <span class="corner corner-top-left"></span>
          <span class="corner corner-top-right"></span>
          <span class="corner corner-bottom-left"></span>
          <span class="corner corner-bottom-right"></span>
          <span class="card-scan"></span>
        </div>
        <div class="auth-head">
          <span class="terminal-dot"></span>
          <div>
            <p>{{ mode === 'login' ? 'ACCOUNT ACCESS' : 'CREATE IDENTITY' }}</p>
            <h1>数融智联岗位能力图谱构建与分析系统</h1>
          </div>
        </div>

        <div class="mode-switch">
          <button :class="{ active: mode === 'login' }" @click="mode = 'login'">登录</button>
          <button :class="{ active: mode === 'register' }" @click="mode = 'register'">注册</button>
        </div>

        <transition name="panel-fade" mode="out-in">
          <el-form v-if="mode === 'login'" key="login" class="auth-form" label-position="top">
            <el-form-item label="用户名">
              <el-input v-model="loginForm.username" size="large" placeholder="hr_admin / student_demo">
                <template #prefix><el-icon><User /></el-icon></template>
              </el-input>
            </el-form-item>
            <el-form-item label="密码">
              <el-input v-model="loginForm.password" size="large" type="password" show-password placeholder="默认 Demo@123" @keyup.enter="submitLogin">
                <template #prefix><el-icon><Lock /></el-icon></template>
              </el-input>
            </el-form-item>

            <button class="neon-button" type="button" :disabled="loading" @click="submitLogin">
              <span>{{ loading ? '正在验证' : '进入系统' }}</span>
              <el-icon><ArrowRight /></el-icon>
            </button>
          </el-form>

          <el-form v-else key="register" class="auth-form register-form" label-position="top">
            <el-form-item label="账号类型">
              <div class="role-segment">
                <button
                  v-for="item in roleOptions"
                  :key="item.value"
                  type="button"
                  :class="{ active: registerForm.role === item.value }"
                  @click="registerForm.role = item.value"
                >
                  {{ item.label }}
                </button>
              </div>
            </el-form-item>
            <el-form-item label="用户名">
              <el-input v-model="registerForm.username" size="large" placeholder="6-20位，需包含英文和数字">
                <template #prefix><el-icon><User /></el-icon></template>
              </el-input>
            </el-form-item>
            <el-form-item label="真实姓名">
              <el-input v-model="registerForm.display_name" size="large" placeholder="请输入真实姓名">
                <template #prefix><el-icon><MagicStick /></el-icon></template>
              </el-input>
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="registerForm.email" size="large" placeholder="用于账号通知和后续验证">
                <template #prefix><el-icon><Message /></el-icon></template>
              </el-input>
            </el-form-item>
            <el-form-item label="组织 / 学校 / 企业">
              <el-input v-model="registerForm.organization" size="large" placeholder="可后续在账号设置中修改">
                <template #prefix><el-icon><OfficeBuilding /></el-icon></template>
              </el-input>
            </el-form-item>
            <el-form-item label="密码">
              <el-input v-model="registerForm.password" size="large" type="password" show-password placeholder="8-32位，含数字并搭配字母或特殊符号">
                <template #prefix><el-icon><Lock /></el-icon></template>
              </el-input>
              <div class="rule-hint">
                <span :class="{ pass: passwordChecks.length }">8-32位</span>
                <span :class="{ pass: passwordChecks.digit }">数字</span>
                <span :class="{ pass: passwordChecks.extra }">大写/小写/特殊符号任一</span>
              </div>
            </el-form-item>
            <el-form-item label="确认密码">
              <el-input v-model="registerForm.confirm_password" size="large" type="password" show-password placeholder="再次输入密码">
                <template #prefix><el-icon><Lock /></el-icon></template>
              </el-input>
            </el-form-item>
            <el-form-item label="验证码">
              <div class="captcha-row">
                <div class="captcha-question">{{ captcha.question || '生成中...' }}</div>
                <el-input v-model="registerForm.captcha_answer" size="large" placeholder="结果" @keyup.enter="submitRegister" />
                <button class="captcha-refresh" type="button" @click="loadCaptcha">
                  <el-icon><Refresh /></el-icon>
                </button>
              </div>
            </el-form-item>

            <button class="neon-button" type="button" :disabled="loading" @click="submitRegister">
              <span>{{ loading ? '正在创建' : '创建并进入' }}</span>
              <el-icon><ArrowRight /></el-icon>
            </button>
          </el-form>
        </transition>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowRight, Lock, MagicStick, Message, OfficeBuilding, Refresh, User } from '@element-plus/icons-vue'
import { api } from '@/api/http'
import { useAuthStore } from '@/stores/auth'

const mode = ref('login')
const loading = ref(false)
const cardTiltStyle = ref<Record<string, string>>({})
const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const roleOptions = [
  { label: '求职者 / 学生', value: 'candidate' },
  { label: '企业 HR', value: 'hr' }
]

const loginForm = reactive({ username: 'hr_admin', password: 'Demo@123' })
const registerForm = reactive({
  username: '',
  password: '',
  confirm_password: '',
  role: 'candidate',
  display_name: '',
  organization: '',
  email: '',
  phone: '',
  captcha_token: '',
  captcha_answer: ''
})
const captcha = reactive({
  question: '',
  token: ''
})
const usernamePattern = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d_]{6,20}$/
const emailPattern = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/
const specialPattern = /[!@#$%^&*()_\-+=[\]{};:'",.<>/?\\|`~]/
const passwordChecks = computed(() => ({
  length: registerForm.password.length >= 8 && registerForm.password.length <= 32,
  digit: /\d/.test(registerForm.password),
  extra: /[A-Z]/.test(registerForm.password) || /[a-z]/.test(registerForm.password) || specialPattern.test(registerForm.password)
}))

onMounted(() => {
  document.documentElement.classList.add('login-active')
  document.body.classList.add('login-active')
  loadCaptcha()
})

onBeforeUnmount(() => {
  document.documentElement.classList.remove('login-active')
  document.body.classList.remove('login-active')
})

function particleStyle(index: number) {
  const left = (index * 37) % 100
  const top = (index * 53) % 100
  const delay = (index % 9) * -0.7
  const size = 2 + (index % 4)
  const duration = 10 + (index % 11) * 1.45
  return {
    left: `${left}%`,
    top: `${top}%`,
    width: `${size}px`,
    height: `${size}px`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`
  }
}

function handlePointerMove(event: PointerEvent) {
  const centerX = window.innerWidth / 2
  const centerY = window.innerHeight / 2
  const rotateY = Math.max(-7, Math.min(7, (event.clientX - centerX) / 52))
  const rotateX = Math.max(-6, Math.min(6, (centerY - event.clientY) / 58))
  cardTiltStyle.value = {
    transform: `perspective(1100px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(0)`
  }
}

function resetTilt() {
  cardTiltStyle.value = {
    transform: 'perspective(1100px) rotateX(0deg) rotateY(0deg)'
  }
}

async function submitLogin() {
  loading.value = true
  try {
    const user = await auth.login(loginForm.username, loginForm.password)
    ElMessage.success('登录成功')
    router.push((route.query.redirect as string) || (user.role === 'candidate' ? '/personal-center' : '/overview'))
  } finally {
    loading.value = false
  }
}

async function loadCaptcha() {
  const data = await api.captcha()
  captcha.question = data.question
  captcha.token = data.token
  registerForm.captcha_token = data.token
  registerForm.captcha_answer = ''
}

function validateRegisterForm() {
  if (!usernamePattern.test(registerForm.username.trim())) {
    ElMessage.warning('用户名需为 6-20 位，且至少包含英文字母和数字，可使用下划线')
    return false
  }
  if (!registerForm.display_name.trim()) {
    ElMessage.warning('请填写真实姓名')
    return false
  }
  if (!emailPattern.test(registerForm.email.trim())) {
    ElMessage.warning('请输入有效邮箱地址')
    return false
  }
  if (!passwordChecks.value.length || !passwordChecks.value.digit || !passwordChecks.value.extra) {
    ElMessage.warning('密码需为 8-32 位，包含数字，并在大写字母、小写字母、特殊符号中至少包含一种')
    return false
  }
  if (registerForm.password !== registerForm.confirm_password) {
    ElMessage.warning('两次输入的密码不一致')
    return false
  }
  if (!registerForm.captcha_answer.trim()) {
    ElMessage.warning('请输入验证码结果')
    return false
  }
  return true
}

async function submitRegister() {
  if (!validateRegisterForm()) return
  loading.value = true
  try {
    const user = await auth.register(registerForm)
    ElMessage.success('账号创建成功')
    router.push(user.role === 'candidate' ? '/personal-center' : '/overview')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '账号创建失败')
    await loadCaptcha()
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
:global(html.login-active),
:global(body.login-active) {
  min-width: 0;
}

:global(body.login-active::before),
:global(body.login-active::after) {
  display: none;
}

.login-page {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  background:
    linear-gradient(135deg, rgba(5, 18, 44, 0.2) 0%, rgba(5, 31, 66, 0.34) 54%, rgba(4, 18, 42, 0.48) 100%),
    radial-gradient(circle at 50% 50%, rgba(0, 175, 255, 0.14), transparent 34%),
    url('../assets/login-background.png') center center / cover no-repeat,
    linear-gradient(135deg, #07091b 0%, #061831 45%, #031024 100%);
  color: #eaf6ff;
  perspective: 1100px;
}

.login-page::before,
.login-page::after {
  position: absolute;
  inset: 0;
  pointer-events: none;
  content: "";
}

.login-page::before {
  opacity: 0.18;
  background:
    linear-gradient(rgba(0, 150, 255, 0.09) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 150, 255, 0.09) 1px, transparent 1px);
  background-size: 42px 42px;
  mask-image: radial-gradient(circle at center, #000 0%, transparent 74%);
}

.aurora {
  position: absolute;
  width: 48vw;
  height: 48vw;
  border-radius: 50%;
  filter: blur(54px);
  opacity: 0.36;
  mix-blend-mode: screen;
  pointer-events: none;
}

.aurora-a {
  left: -16vw;
  top: -20vw;
  background: radial-gradient(circle, rgba(0, 194, 255, 0.74), transparent 62%);
  animation: floatAurora 12s ease-in-out infinite;
}

.aurora-b {
  right: -18vw;
  bottom: -18vw;
  background: radial-gradient(circle, rgba(62, 115, 255, 0.62), transparent 64%);
  animation: floatAurora 14s ease-in-out infinite reverse;
}

.scan-line {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: repeating-linear-gradient(0deg, rgba(255, 255, 255, 0.032) 0 1px, transparent 1px 5px);
  opacity: 0.1;
}

.matrix-grid {
  position: absolute;
  left: 18%;
  bottom: -24%;
  width: 64vw;
  height: 44vh;
  border-radius: 50%;
  background: linear-gradient(rgba(46, 189, 255, 0.18) 1px, transparent 1px), linear-gradient(90deg, rgba(46, 189, 255, 0.18) 1px, transparent 1px);
  background-size: 38px 38px;
  transform: perspective(760px) rotateX(62deg);
  transform-origin: center bottom;
  opacity: 0.16;
  animation: gridMove 10s linear infinite;
}

.particle-field {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.particle-field i {
  position: absolute;
  border-radius: 50%;
  background: rgba(88, 207, 255, 0.9);
  filter: blur(0.4px);
  box-shadow: 0 0 14px rgba(78, 207, 255, 0.62);
  opacity: 0;
  animation: particleDrift 14s linear infinite;
}

.login-stage {
  position: relative;
  z-index: 1;
  display: grid;
  place-items: center;
  min-height: 100vh;
  padding: 42px 20px;
}

.orbit-shell {
  position: absolute;
  left: 50%;
  top: 50%;
  width: min(92vw, 940px);
  height: min(92vw, 940px);
  transform: translate(-50%, -50%);
  pointer-events: none;
}

.orbit-shell::before {
  position: absolute;
  inset: 23%;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(0, 150, 255, 0.18), rgba(7, 31, 58, 0.14) 58%, transparent 70%);
  box-shadow: 0 0 130px rgba(0, 150, 255, 0.24);
  content: "";
}

.orbit-ring {
  position: absolute;
  border-radius: 50%;
  border: 1px solid rgba(130, 226, 255, 0.22);
  box-shadow: inset 0 0 28px rgba(96, 214, 255, 0.08), 0 0 34px rgba(96, 214, 255, 0.08);
}

.ring-outer {
  inset: 0;
  border-color: rgba(119, 218, 255, 0.2);
  animation: rotateRing 24s linear infinite;
}

.ring-middle {
  inset: 13%;
  border: 0;
  background: repeating-conic-gradient(from 0deg, rgba(118, 226, 255, 0.28) 0deg 6deg, transparent 6deg 15deg);
  -webkit-mask: radial-gradient(farthest-side, transparent calc(100% - 1px), #000 calc(100% - 1px));
  mask: radial-gradient(farthest-side, transparent calc(100% - 1px), #000 calc(100% - 1px));
  opacity: 0.72;
  animation: rotateRing 28s linear infinite reverse;
}

.ring-dashed {
  inset: 23%;
  border: 0;
  background: repeating-conic-gradient(from 0deg, rgba(145, 238, 255, 0.44) 0deg 7deg, transparent 7deg 16deg);
  -webkit-mask: radial-gradient(farthest-side, transparent calc(100% - 2px), #000 calc(100% - 2px));
  mask: radial-gradient(farthest-side, transparent calc(100% - 2px), #000 calc(100% - 2px));
  opacity: 0.6;
  animation: rotateRing 12s linear infinite;
}

.ring-inner {
  inset: 28%;
  border: 0;
  background: repeating-conic-gradient(from 0deg, rgba(190, 247, 255, 0.42) 0deg 8deg, transparent 8deg 18deg);
  -webkit-mask: radial-gradient(farthest-side, transparent calc(100% - 1px), #000 calc(100% - 1px));
  mask: radial-gradient(farthest-side, transparent calc(100% - 1px), #000 calc(100% - 1px));
  opacity: 0.58;
  animation: rotateRing 9s linear infinite reverse;
}

.orbit-runner {
  position: absolute;
  left: 50%;
  top: 50%;
  border-radius: 50%;
  pointer-events: none;
}

.orbit-runner i {
  position: absolute;
  right: -4px;
  top: 50%;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #8ff3ff;
  box-shadow: 0 0 18px #8ff3ff, 0 0 36px rgba(0, 150, 255, 0.9);
  transform: translateY(-50%);
}

.runner-a {
  width: 100%;
  height: 100%;
  margin: -50% 0 0 -50%;
  animation: orbitParticle 9s linear infinite;
}

.runner-b {
  width: 74%;
  height: 74%;
  margin: -37% 0 0 -37%;
  animation: orbitParticle 13s linear infinite reverse;
}

.runner-b i {
  width: 7px;
  height: 7px;
  background: #43dcff;
}

.runner-c {
  width: 54%;
  height: 54%;
  margin: -27% 0 0 -27%;
  animation: orbitParticle 7.2s linear infinite;
}

.runner-c i {
  width: 6px;
  height: 6px;
  background: #ffffff;
}

.orbit-dot {
  position: absolute;
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: #8ff3ff;
  box-shadow: 0 0 24px #8ff3ff;
}

.dot-a {
  left: 50%;
  top: -4px;
  animation: dotFloat 4s ease-in-out infinite;
}

.dot-b {
  right: 12%;
  bottom: 22%;
  animation: dotFloat 4.8s ease-in-out infinite -1.2s;
}

.dot-c {
  left: 18%;
  bottom: 26%;
  animation: dotFloat 5.2s ease-in-out infinite -2.2s;
}

.orbit-cross {
  position: absolute;
  width: 140px;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(132, 232, 255, 0.42), transparent);
}

.cross-a {
  left: 5%;
  top: 46%;
  transform: rotate(18deg);
}

.cross-b {
  right: 3%;
  top: 55%;
  transform: rotate(-24deg);
}

.auth-card {
  position: relative;
  width: min(92vw, 464px);
  max-height: calc(100vh - 84px);
  overflow-x: hidden;
  overflow-y: auto;
  border: 1px solid rgba(102, 207, 255, 0.32);
  border-radius: 18px;
  padding: 34px;
  background: linear-gradient(145deg, rgba(15, 34, 68, 0.72), rgba(13, 55, 96, 0.56));
  box-shadow: 0 0 28px rgba(64, 188, 255, 0.2), 0 30px 82px rgba(0, 0, 0, 0.34), inset 0 1px 0 rgba(255, 255, 255, 0.16);
  backdrop-filter: blur(18px);
  transform-style: preserve-3d;
  transition: transform 0.18s ease, box-shadow 0.28s ease, border-color 0.28s ease;
  will-change: transform;
  scrollbar-width: thin;
  scrollbar-color: rgba(83, 220, 255, 0.42) transparent;
}

.auth-card:hover {
  border-color: rgba(121, 226, 255, 0.48);
  box-shadow: 0 0 44px rgba(69, 198, 255, 0.3), 0 30px 82px rgba(0, 0, 0, 0.36), inset 0 1px 0 rgba(255, 255, 255, 0.18);
}

.auth-card::-webkit-scrollbar {
  width: 3px;
  height: 0;
}

.auth-card::-webkit-scrollbar-track,
.auth-card::-webkit-scrollbar-corner {
  background: transparent;
}

.auth-card::-webkit-scrollbar-thumb {
  border-radius: 99px;
  background: rgba(83, 220, 255, 0.46);
}

.auth-card.auth-register {
  padding-bottom: 28px;
}

.tech-decoration {
  position: absolute;
  inset: 0;
  z-index: 0;
  overflow: hidden;
  border-radius: inherit;
  pointer-events: none;
}

.corner {
  position: absolute;
  width: 30px;
  height: 30px;
  border: 2px solid rgba(0, 150, 255, 0.78);
  opacity: 0.8;
}

.corner-top-left {
  left: 12px;
  top: 12px;
  border-right: none;
  border-bottom: none;
}

.corner-top-right {
  right: 12px;
  top: 12px;
  border-left: none;
  border-bottom: none;
}

.corner-bottom-left {
  left: 12px;
  bottom: 12px;
  border-right: none;
  border-top: none;
}

.corner-bottom-right {
  right: 12px;
  bottom: 12px;
  border-left: none;
  border-top: none;
}

.card-scan {
  position: absolute;
  left: 20px;
  right: 20px;
  top: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(105, 228, 255, 0.72), transparent);
  opacity: 0.44;
  box-shadow: 0 0 14px rgba(68, 202, 255, 0.36);
  animation: cardScan 4s linear infinite;
}

.auth-register .corner-bottom-left,
.auth-register .corner-bottom-right {
  opacity: 0;
}

.auth-head {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: flex-start;
  gap: 14px;
  margin-bottom: 24px;
}

.terminal-dot {
  flex: 0 0 auto;
  width: 14px;
  height: 14px;
  margin-top: 9px;
  border-radius: 50%;
  background: #51f2ff;
  box-shadow: 0 0 22px #51f2ff;
}

.auth-head p {
  margin: 0;
  color: rgba(142, 228, 255, 0.78);
  font-size: 11px;
  font-weight: 950;
  letter-spacing: 0.22em;
}

.auth-head h1 {
  margin: 8px 0 0;
  color: #fff;
  font-size: 25px;
  font-weight: 950;
  line-height: 1.25;
}

.mode-switch {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 22px;
  border: 1px solid rgba(128, 224, 255, 0.26);
  border-radius: 18px;
  padding: 6px;
  background: rgba(14, 36, 70, 0.38);
}

.mode-switch button,
.role-segment button,
.neon-button {
  font-family: inherit;
}

.mode-switch button {
  border: 0;
  border-radius: 13px;
  padding: 11px 10px;
  background: transparent;
  color: rgba(205, 236, 249, 0.72);
  font-weight: 900;
  cursor: pointer;
  transition: 0.25s ease;
}

.mode-switch button.active {
  background: linear-gradient(135deg, rgba(30, 136, 255, 0.94), rgba(31, 212, 255, 0.76));
  color: #fff;
  box-shadow: 0 10px 28px rgba(28, 178, 255, 0.28);
}

.auth-form {
  position: relative;
  z-index: 1;
}

.auth-form :deep(.el-form-item) {
  margin-bottom: 17px;
}

.auth-form :deep(.el-form-item__label) {
  color: rgba(211, 238, 250, 0.76);
  font-weight: 850;
}

.auth-form :deep(.el-input__wrapper) {
  border: 1px solid rgba(132, 222, 255, 0.24);
  border-radius: 16px;
  background: rgba(13, 36, 72, 0.5);
  box-shadow: inset 0 0 0 1px transparent, 0 12px 24px rgba(0, 0, 0, 0.08);
  transition: 0.24s ease;
}

.auth-form :deep(.el-input__wrapper.is-focus) {
  border-color: rgba(87, 231, 255, 0.72);
  box-shadow: 0 0 0 3px rgba(70, 202, 255, 0.14), 0 0 26px rgba(69, 203, 255, 0.18);
}

.auth-form :deep(.el-input__inner) {
  color: #f4fbff;
  font-weight: 800;
}

.auth-form :deep(.el-input__inner::placeholder) {
  color: rgba(186, 223, 242, 0.42);
}

.auth-form :deep(.el-icon) {
  color: #6ce9ff;
}

.neon-button {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  min-height: 50px;
  overflow: hidden;
  border: 0;
  border-radius: 17px;
  background: linear-gradient(135deg, #1779ff, #00d7ff);
  color: #fff;
  font-size: 16px;
  font-weight: 950;
  cursor: pointer;
  box-shadow: 0 16px 34px rgba(0, 179, 255, 0.32), inset 0 1px 0 rgba(255, 255, 255, 0.35);
  transition: transform 0.22s ease, box-shadow 0.22s ease, filter 0.22s ease;
}

.neon-button::before {
  position: absolute;
  top: -40%;
  left: -30%;
  width: 34%;
  height: 180%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.68), transparent);
  transform: rotate(18deg);
  animation: buttonShine 3.6s ease-in-out infinite;
  content: "";
}

.neon-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 22px 44px rgba(0, 194, 255, 0.42), 0 0 34px rgba(77, 225, 255, 0.28);
  filter: saturate(1.08);
}

.neon-button:disabled {
  cursor: progress;
  opacity: 0.78;
}

.role-segment {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.role-segment button {
  min-height: 42px;
  border: 1px solid rgba(122, 219, 255, 0.22);
  border-radius: 16px;
  background: rgba(5, 24, 50, 0.62);
  color: rgba(218, 243, 255, 0.74);
  font-weight: 900;
  cursor: pointer;
  transition: 0.22s ease;
}

.role-segment button:hover {
  border-color: rgba(96, 232, 255, 0.62);
  background: rgba(12, 79, 121, 0.55);
  transform: translateY(-1px);
}

.role-segment button.active {
  border-color: rgba(88, 231, 255, 0.72);
  background: rgba(18, 116, 168, 0.74);
  color: #fff;
  box-shadow: 0 0 24px rgba(56, 207, 255, 0.18);
}

.rule-hint {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  margin-top: 9px;
}

.rule-hint span {
  border: 1px solid rgba(122, 219, 255, 0.18);
  border-radius: 999px;
  padding: 4px 8px;
  background: rgba(3, 18, 39, 0.45);
  color: rgba(188, 224, 240, 0.56);
  font-size: 11px;
  font-weight: 850;
  transition: 0.2s ease;
}

.rule-hint span.pass {
  border-color: rgba(72, 231, 255, 0.55);
  background: rgba(16, 122, 158, 0.42);
  color: #aff5ff;
  box-shadow: 0 0 16px rgba(56, 207, 255, 0.16);
}

.captcha-row {
  display: grid;
  grid-template-columns: minmax(108px, 0.8fr) minmax(96px, 1fr) 46px;
  gap: 10px;
  width: 100%;
}

.captcha-question,
.captcha-refresh {
  display: grid;
  place-items: center;
  min-height: 40px;
  border: 1px solid rgba(122, 219, 255, 0.24);
  border-radius: 15px;
  background: rgba(13, 36, 72, 0.5);
  color: #dff8ff;
  font-weight: 950;
}

.captcha-refresh {
  cursor: pointer;
  transition: 0.22s ease;
}

.captcha-refresh:hover {
  border-color: rgba(88, 231, 255, 0.72);
  background: rgba(18, 116, 168, 0.74);
  color: #fff;
  transform: rotate(90deg);
}

.panel-fade-enter-active,
.panel-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.panel-fade-enter-from,
.panel-fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

@keyframes floatAurora {
  0%,
  100% {
    transform: translate3d(0, 0, 0) scale(1);
  }
  50% {
    transform: translate3d(7vw, 4vh, 0) scale(1.12);
  }
}

@keyframes gridMove {
  from {
    background-position: 0 0, 0 0;
  }
  to {
    background-position: 0 38px, 38px 0;
  }
}

@keyframes particleDrift {
  0%,
  100% {
    opacity: 0.12;
    transform: translate3d(0, 0, 0) scale(0.72);
  }
  50% {
    opacity: 0.78;
    transform: translate3d(82px, -96px, 0) scale(1);
  }
}

@keyframes rotateRing {
  to {
    transform: rotate(360deg);
  }
}

@keyframes orbitParticle {
  to {
    transform: rotate(360deg);
  }
}

@keyframes pulseRing {
  0%,
  100% {
    opacity: 0.64;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.025);
  }
}

@keyframes dotFloat {
  0%,
  100% {
    opacity: 0.7;
    transform: translateY(0);
  }
  50% {
    opacity: 1;
    transform: translateY(-12px);
  }
}

@keyframes cardScan {
  from {
    transform: translateY(0);
  }
  to {
    transform: translateY(720px);
  }
}

@keyframes buttonShine {
  0%,
  48% {
    left: -42%;
  }
  72%,
  100% {
    left: 120%;
  }
}

@media (max-width: 760px) {
  .orbit-shell {
    width: 126vw;
    height: 126vw;
  }

  .auth-card {
    padding: 24px;
  }

  .auth-head h1 {
    font-size: 21px;
  }
}

@media (max-width: 520px) {
  .login-stage {
    padding: 24px 16px;
  }

  .orbit-shell {
    width: 152vw;
    height: 152vw;
  }

  .auth-card {
    width: 100%;
    border-radius: 24px;
    padding: 22px;
  }

  .captcha-row {
    grid-template-columns: 1fr 1fr 44px;
  }
}
</style>
