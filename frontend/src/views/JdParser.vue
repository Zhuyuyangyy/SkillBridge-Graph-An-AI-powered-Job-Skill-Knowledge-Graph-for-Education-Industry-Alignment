<template>
  <div class="page">
    <PageHeader title="JD解析" desc="输入岗位 JD 文本，提取岗位名称、职责、技能、工具、证书、场景和证据来源">
      <el-button type="primary" :loading="loading" @click="submit">解析 JD</el-button>
    </PageHeader>
    <div class="content-grid">
      <div class="panel span-5">
        <el-input v-model="text" type="textarea" :rows="18" placeholder="请输入 JD 文本" />
      </div>
      <div class="panel span-7">
        <el-empty v-if="!result" description="解析结果将在这里展示" />
        <template v-else>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="岗位名称">{{ result.job_name }}</el-descriptions-item>
            <el-descriptions-item label="所属领域">{{ result.domain }}</el-descriptions-item>
            <el-descriptions-item label="岗位等级">{{ result.level }}</el-descriptions-item>
            <el-descriptions-item label="经验要求">{{ result.experience }}</el-descriptions-item>
            <el-descriptions-item label="置信度">{{ result.confidence }}</el-descriptions-item>
            <el-descriptions-item label="防控状态">{{ result.guard_status }}</el-descriptions-item>
          </el-descriptions>
          <h3>核心职责</h3>
          <el-timeline>
            <el-timeline-item v-for="item in result.responsibilities" :key="item">{{ item }}</el-timeline-item>
          </el-timeline>
          <h3>必备技能</h3>
          <div class="tag-list"><el-tag v-for="item in result.required_skills" :key="item">{{ item }}</el-tag></div>
          <h3>加分技能与工具平台</h3>
          <div class="tag-list">
            <el-tag v-for="item in [...result.preferred_skills, ...result.tools]" :key="item" type="info">{{ item }}</el-tag>
          </div>
          <h3>证据来源</h3>
          <el-table :data="result.evidence_sources" size="small">
            <el-table-column prop="source" label="来源" />
            <el-table-column prop="quote" label="证据片段" />
          </el-table>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import { api } from '@/api/http'

const loading = ref(false)
const result = ref<any>()
const text = ref('大模型应用工程师，负责企业知识库 RAG 应用建设，需要 Python、FastAPI、LangChain、向量数据库、Docker、Prompt Engineering，熟悉智能制造或智慧教育场景。')

async function submit() {
  loading.value = true
  try {
    result.value = await api.parseJd(text.value)
  } catch {
    ElMessage.error('解析失败，请确认后端服务已启动')
  } finally {
    loading.value = false
  }
}
</script>
