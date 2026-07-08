<template>
  <div class="page">
    <PageHeader title="候选人管理" desc="企业 HR 可查看求职者提交的个人画像、简历、技能证书和匹配准备情况" />
    <div class="panel">
      <el-table :data="rows" stripe>
        <el-table-column label="候选人" min-width="170">
          <template #default="{ row }">
            <b>{{ row.profile.real_name || row.user?.display_name }}</b>
            <div class="sub">{{ row.user?.username }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="profile.target_role" label="目标岗位" min-width="170" />
        <el-table-column label="学校" min-width="190">
          <template #default="{ row }">
            <div class="school-cell">
              <b>{{ row.profile.school || '-' }}</b>
              <span class="school-tags">
                <span v-for="badge in schoolBadges(row.profile.school)" :key="badge" class="elite-badge" :class="eliteBadgeClass(badge)">{{ badge }}</span>
              </span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="学历" width="128">
          <template #default="{ row }">
            <span class="education-cell">{{ row.profile.education || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="技能" min-width="260">
          <template #default="{ row }">
            <el-tag v-for="skill in row.profile.skills.slice(0, 4)" :key="skill" type="primary">{{ skill }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="完整度" width="150">
          <template #default="{ row }">
            <el-progress :percentage="row.profile.completeness" />
          </template>
        </el-table-column>
        <el-table-column prop="resume_count" label="简历数" width="90" />
        <el-table-column label="操作" width="110">
          <template #default="{ row }">
            <el-button type="primary" link @click="current = row; visible = true">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="visible" class="tech-dialog candidate-dialog" width="900px" align-center>
      <template #header>
        <span></span>
      </template>
      <div v-if="current" class="candidate-detail">
        <section class="candidate-hero">
          <div class="candidate-avatar">
            <img v-if="current.profile.avatar_url" :src="current.profile.avatar_url" alt="候选人头像" />
            <span v-else>{{ candidateInitial(current) }}</span>
          </div>
          <div class="candidate-main">
            <div class="candidate-title-row">
              <div>
                <h3>{{ current.profile.real_name || current.user?.display_name }}</h3>
                <p>{{ current.user?.username }} · {{ current.profile.education || '学历未填写' }} · {{ current.profile.major || '专业未填写' }}</p>
              </div>
              <el-tag type="primary" effect="light">{{ current.profile.target_role || '目标岗位未填写' }}</el-tag>
            </div>
            <div class="candidate-summary">{{ current.profile.self_summary || '候选人还没有填写个人总结。' }}</div>
          </div>
          <div class="candidate-complete">
            <strong>{{ current.profile.completeness || 0 }}%</strong>
            <span>画像完整度</span>
          </div>
        </section>

        <div class="detail-grid">
          <article>
            <span>学校</span>
            <b>{{ current.profile.school || '-' }}</b>
            <p class="detail-tags">
              <span v-for="badge in schoolBadges(current.profile.school)" :key="badge" class="elite-badge" :class="eliteBadgeClass(badge)">{{ badge }}</span>
            </p>
          </article>
          <article><span>专业方向</span><b>{{ current.profile.major || '-' }}</b></article>
          <article><span>意向城市</span><b>{{ formatCityDisplay(current.profile.city) || '-' }}</b></article>
          <article><span>期望薪资</span><b>{{ current.profile.expected_salary || '-' }}</b></article>
        </div>

        <section class="candidate-section">
          <div class="section-title">
            <h4>能力与证书</h4>
            <span>{{ current.profile.skills.length }} 项能力 · {{ current.profile.certificates.length }} 项证书</span>
          </div>
          <div class="skill-zone">
            <div class="tag-panel">
              <b>能力标签</b>
              <div class="tag-list">
                <el-tag v-for="item in current.profile.skills" :key="item" type="primary">{{ item }}</el-tag>
                <span v-if="!current.profile.skills.length" class="empty-inline">暂无能力标签</span>
              </div>
            </div>
            <div class="tag-panel">
              <b>证书成果</b>
              <div class="tag-list">
                <el-tag v-for="item in current.profile.certificates" :key="item" type="success">{{ item }}</el-tag>
                <span v-if="!current.profile.certificates.length" class="empty-inline">暂无证书记录</span>
              </div>
            </div>
          </div>
        </section>

        <section class="candidate-section">
          <div class="section-title">
            <h4>经历材料</h4>
            <span>项目、实习、竞赛和最近简历摘要</span>
          </div>
          <div class="experience-grid">
            <div class="experience-block">
              <b>项目经历</b>
              <p v-for="item in current.profile.projects.slice(0, 3)" :key="item">{{ item }}</p>
              <p v-if="!current.profile.projects.length" class="empty-inline">暂无项目经历</p>
            </div>
            <div class="experience-block">
              <b>实习经历</b>
              <p v-for="item in current.profile.internships.slice(0, 3)" :key="item">{{ item }}</p>
              <p v-if="!current.profile.internships.length" class="empty-inline">暂无实习经历</p>
            </div>
            <div class="experience-block">
              <b>竞赛 / 奖项</b>
              <p v-for="item in current.profile.awards.slice(0, 3)" :key="item">{{ item }}</p>
              <p v-if="!current.profile.awards.length" class="empty-inline">暂无竞赛或奖项</p>
            </div>
          </div>
          <div class="resume-snippet">
            <span>最近简历</span>
            <p>{{ current.latest_resume?.projects || '暂无简历记录' }}</p>
          </div>
        </section>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import { api } from '@/api/http'
import { doubleFirstClassUniversities, universities211, universities985 } from '@/data/profileOptions'

const rows = ref<any[]>([])
const visible = ref(false)
const current = ref<any>()

onMounted(async () => {
  rows.value = await api.hrCandidates()
})

function normalizeSchoolName(value = '') {
  return value.replace(/[（(].*?[）)]/g, '').replace(/\s+/g, '').trim()
}

function schoolBadges(school = '') {
  const normalized = normalizeSchoolName(school)
  const badges: string[] = []
  if (!normalized) return badges
  if (universities985.some((name) => normalizeSchoolName(name) === normalized)) badges.push('985')
  if (badges.includes('985') || universities211.some((name) => normalizeSchoolName(name) === normalized)) badges.push('211')
  if (doubleFirstClassUniversities.some((name) => normalizeSchoolName(name) === normalized)) badges.push('双一流')
  return badges
}

function eliteBadgeClass(badge: string) {
  return {
    'elite-badge-985': badge === '985',
    'elite-badge-211': badge === '211',
    'elite-badge-double': badge === '双一流'
  }
}

function candidateInitial(row: any) {
  return (row?.profile?.real_name || row?.user?.display_name || row?.user?.username || '候').slice(0, 1)
}

function formatCityDisplay(value = '') {
  const parts = value.split('/').map((item) => item.trim()).filter(Boolean)
  if (parts.length >= 2 && parts[0] === parts[1]) return parts[0]
  return value
}
</script>

<style scoped>
.sub {
  margin-top: 4px;
  color: #64748b;
  font-size: 12px;
}

.school-cell {
  display: grid;
  gap: 7px;
  justify-items: center;
}

.school-cell b {
  max-width: 170px;
  overflow: hidden;
  color: #14346c;
  font-weight: 900;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.school-tags,
.detail-tags {
  display: inline-flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 5px;
  margin: 0;
}

.education-cell {
  display: inline-block;
  max-width: 108px;
  overflow: hidden;
  color: #14346c;
  font-weight: 850;
  text-overflow: ellipsis;
  vertical-align: middle;
  white-space: nowrap;
}

.candidate-dialog :deep(.el-dialog__header) {
  min-height: 0;
  padding: 0;
}

.candidate-dialog :deep(.el-dialog__body) {
  padding: 0;
}

.candidate-detail {
  padding: 18px;
}

.candidate-hero {
  position: relative;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) 118px;
  gap: 18px;
  overflow: hidden;
  border: 1px solid rgba(190, 213, 242, 0.82);
  border-radius: 22px;
  padding: 18px;
  background:
    radial-gradient(circle at 8% 0%, rgba(6, 182, 212, 0.18), transparent 30%),
    radial-gradient(circle at 86% 16%, rgba(37, 99, 235, 0.14), transparent 26%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.82), rgba(232, 242, 255, 0.62));
}

.candidate-hero::after {
  position: absolute;
  right: -80px;
  top: -90px;
  width: 220px;
  height: 220px;
  content: "";
  border: 1px dashed rgba(6, 182, 212, 0.22);
  border-radius: 50%;
}

.candidate-avatar {
  position: relative;
  z-index: 1;
  display: grid;
  place-items: center;
  width: 86px;
  height: 86px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.92);
  border-radius: 26px;
  background:
    radial-gradient(circle at 32% 18%, rgba(255, 255, 255, 0.95), transparent 28%),
    linear-gradient(135deg, #2563eb, #06b6d4);
  box-shadow: 0 18px 42px rgba(37, 99, 235, 0.18);
  color: #fff;
  font-size: 32px;
  font-weight: 950;
}

.candidate-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.candidate-main,
.candidate-complete {
  position: relative;
  z-index: 1;
}

.candidate-title-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.candidate-title-row h3 {
  margin: 0;
  color: #071a3d;
  font-size: 28px;
  line-height: 1.15;
}

.candidate-title-row p {
  margin: 8px 0 0;
  color: #64748b;
  font-size: 13px;
  font-weight: 750;
}

.candidate-summary {
  margin-top: 16px;
  border: 1px solid rgba(190, 213, 242, 0.68);
  border-radius: 16px;
  padding: 12px 14px;
  background: rgba(255, 255, 255, 0.54);
  color: #334155;
  font-size: 14px;
  font-weight: 650;
  line-height: 1.8;
}

.candidate-complete {
  display: grid;
  place-items: center;
  align-self: stretch;
  border: 1px solid rgba(6, 182, 212, 0.28);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.5);
}

.candidate-complete strong {
  color: #0f2f78;
  font-size: 30px;
  font-weight: 950;
}

.candidate-complete span {
  margin-top: -18px;
  color: #64748b;
  font-size: 12px;
  font-weight: 850;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  margin: 16px 0;
}

.detail-grid article {
  position: relative;
  display: grid;
  grid-template-rows: 22px minmax(42px, 1fr) auto;
  align-items: center;
  min-height: 128px;
  overflow: hidden;
  border: 1px solid rgba(138, 181, 238, 0.62);
  border-radius: 22px;
  padding: 18px;
  background:
    radial-gradient(circle at 8% 0%, rgba(6, 182, 212, 0.18), transparent 36%),
    radial-gradient(circle at 100% 100%, rgba(37, 99, 235, 0.12), transparent 40%),
    linear-gradient(145deg, rgba(255, 255, 255, 0.78), rgba(226, 241, 255, 0.68));
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.72),
    0 14px 34px rgba(37, 99, 235, 0.08);
  transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
}

.detail-grid article::after {
  position: absolute;
  right: -34px;
  bottom: -38px;
  width: 100px;
  height: 100px;
  content: "";
  border: 1px dashed rgba(6, 182, 212, 0.22);
  border-radius: 50%;
}

.detail-grid article:hover {
  border-color: rgba(6, 182, 212, 0.42);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.78),
    0 20px 46px rgba(37, 99, 235, 0.13);
  transform: translateY(-2px);
}

.detail-grid article > span {
  display: block;
  color: #53657e;
  font-size: 14px;
  font-weight: 850;
  text-align: center;
  white-space: nowrap;
}

.detail-grid b {
  display: block;
  margin-top: 8px;
  color: #06285e;
  font-size: 22px;
  font-weight: 950;
  line-height: 1.25;
  text-align: center;
}

.detail-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
  justify-content: center;
}

.detail-tags .elite-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 29px;
  min-width: 58px;
  padding: 0 12px;
  color: #fff;
  font-size: 13px;
  text-align: center;
}

.detail-tags .elite-badge-double {
  min-width: 82px;
}

.school-tags .elite-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  text-align: center;
}

.candidate-section {
  border: 1px solid rgba(190, 213, 242, 0.72);
  border-radius: 20px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.54);
}

.candidate-section + .candidate-section {
  margin-top: 14px;
}

.section-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.section-title h4 {
  margin: 0;
  color: #071a3d;
  font-size: 18px;
}

.section-title span {
  color: #64748b;
  font-size: 12px;
  font-weight: 800;
}

.skill-zone {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.tag-panel,
.experience-block,
.resume-snippet {
  border: 1px solid rgba(190, 213, 242, 0.66);
  border-radius: 17px;
  padding: 13px;
  background: rgba(232, 242, 255, 0.42);
}

.tag-panel b,
.experience-block b,
.resume-snippet span {
  display: block;
  margin-bottom: 10px;
  color: #14346c;
  font-weight: 950;
}

.tag-list {
  align-items: flex-start;
}

.empty-inline {
  color: #8a9bb1;
  font-size: 13px;
  font-weight: 750;
}

.experience-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.experience-block p,
.resume-snippet p {
  margin: 7px 0 0;
  color: #334155;
  font-size: 13px;
  font-weight: 650;
  line-height: 1.75;
}

.resume-snippet {
  margin-top: 12px;
}
</style>
