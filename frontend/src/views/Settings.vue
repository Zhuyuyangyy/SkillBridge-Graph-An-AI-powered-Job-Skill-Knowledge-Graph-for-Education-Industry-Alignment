<template>
  <div class="page">
    <PageHeader title="系统设置" desc="管理智能服务配置、图谱写入规则和审核阈值" />
    <div class="content-grid">
      <div class="panel span-6">
        <h3>智能服务配置</h3>
        <el-form label-width="130px">
          <el-form-item label="当前服务">
            <el-tag :type="ai.enabled ? 'success' : 'primary'">{{ providerLabel }}</el-tag>
          </el-form-item>
          <el-form-item label="模型名称">
            <el-input :model-value="modelLabel" disabled />
          </el-form-item>
          <el-form-item label="接口状态">
            <el-tag :type="ai.enabled ? 'success' : 'warning'">
              {{ ai.enabled ? '外部服务已启用' : '本地智能服务运行中' }}
            </el-tag>
          </el-form-item>
          <el-form-item label="支持任务">
            <div class="tag-list">
              <el-tag v-for="item in ai.supported_tasks || []" :key="item" type="info">{{ item }}</el-tag>
            </div>
          </el-form-item>
        </el-form>
        <el-alert
          style="margin-top: 14px"
          title="切换外部模型服务时，在环境变量中配置服务地址、密钥和模型名称即可。"
          type="info"
          :closable="false"
        />
      </div>
      <div class="panel span-6">
        <h3>图谱写入规则</h3>
        <el-checkbox v-model="rules.evidence">写入岗位定义、技能关系、更新记录时必须带 evidence</el-checkbox>
        <el-checkbox v-model="rules.review">低置信度内容进入人工审核</el-checkbox>
        <el-checkbox v-model="rules.version">岗位能力更新保留版本记录</el-checkbox>
        <el-form label-width="130px" style="margin-top: 18px">
          <el-form-item label="低置信度阈值">
            <el-slider v-model="threshold" :min="50" :max="95" />
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import { api } from '@/api/http'

const threshold = ref(72)
const ai = ref<any>({})
const providerLabel = computed(() => (ai.value.provider === 'mock' ? '本地智能服务' : ai.value.provider || '本地智能服务'))
const modelLabel = computed(() => (ai.value.provider === 'mock' ? '本地规则与模型适配层' : ai.value.model || '模型服务'))
const rules = reactive({
  evidence: true,
  review: true,
  version: true
})

onMounted(async () => {
  ai.value = await api.aiStatus()
})
</script>
