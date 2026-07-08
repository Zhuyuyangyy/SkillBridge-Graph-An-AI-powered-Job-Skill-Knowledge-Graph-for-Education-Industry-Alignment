<template>
  <div class="page">
    <PageHeader title="账号设置" desc="维护账号资料、联系方式和登录密码" />
    <div class="content-grid">
      <div class="panel span-6">
        <h3>账号资料</h3>
        <el-form label-width="100px">
          <el-form-item label="用户名"><el-input :model-value="auth.user?.username" disabled /></el-form-item>
          <el-form-item label="角色"><el-input :model-value="roleLabel" disabled /></el-form-item>
          <el-form-item label="显示名称"><el-input v-model="account.display_name" /></el-form-item>
          <el-form-item label="邮箱"><el-input v-model="account.email" /></el-form-item>
          <el-form-item label="手机"><el-input v-model="account.phone" /></el-form-item>
          <el-form-item label="组织"><el-input v-model="account.organization" /></el-form-item>
        </el-form>
        <el-button type="primary" :loading="savingAccount" @click="saveAccount">保存资料</el-button>
      </div>
      <div class="panel span-6">
        <h3>修改密码</h3>
        <el-form label-width="100px">
          <el-form-item label="原密码"><el-input v-model="password.old_password" type="password" show-password /></el-form-item>
          <el-form-item label="新密码"><el-input v-model="password.new_password" type="password" show-password /></el-form-item>
          <el-form-item label="确认密码"><el-input v-model="password.confirm_new_password" type="password" show-password /></el-form-item>
        </el-form>
        <el-alert title="修改密码后会清除当前登录会话，需要重新登录。" type="warning" :closable="false" />
        <el-button style="margin-top: 16px" type="primary" :loading="savingPassword" @click="changePassword">确认修改</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import { api } from '@/api/http'
import { useAuthStore } from '@/stores/auth'
import { ref } from 'vue'

const auth = useAuthStore()
const router = useRouter()
const savingAccount = ref(false)
const savingPassword = ref(false)
const account = reactive({
  display_name: auth.user?.display_name || '',
  email: auth.user?.email || '',
  phone: auth.user?.phone || '',
  organization: auth.user?.organization || ''
})
const password = reactive({ old_password: '', new_password: '', confirm_new_password: '' })
const roleLabel = computed(() => (auth.role === 'hr' ? '企业 HR' : auth.role === 'admin' ? '管理员' : '求职者/学生'))

async function saveAccount() {
  savingAccount.value = true
  try {
    const user = await api.updateAccount(account)
    auth.setSession(auth.token, user)
    ElMessage.success('账号资料已保存')
  } finally {
    savingAccount.value = false
  }
}

async function changePassword() {
  if (password.new_password !== password.confirm_new_password) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }
  savingPassword.value = true
  try {
    await api.changePassword(password)
    ElMessage.success('密码已修改，请重新登录')
    await auth.logout()
    router.push('/login')
  } finally {
    savingPassword.value = false
  }
}
</script>
