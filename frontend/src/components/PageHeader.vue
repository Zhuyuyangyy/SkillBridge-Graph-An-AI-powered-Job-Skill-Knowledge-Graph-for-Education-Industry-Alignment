<template>
  <div v-if="$slots.default" class="page-toolbar" aria-label="页面操作">
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{ title: string; desc?: string }>()
</script>

<style scoped>
.page-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  margin-bottom: 18px;
  border: 1px solid rgba(113, 177, 255, 0.3);
  border-radius: 18px;
  padding: 12px 14px;
  background:
    radial-gradient(circle at 12% 0%, rgba(0, 200, 245, 0.12), transparent 32%),
    rgba(255, 255, 255, 0.68);
  box-shadow: 0 14px 36px rgba(24, 96, 188, 0.08);
  backdrop-filter: blur(16px);
}

.page-toolbar :deep(.el-button--primary) {
  border: 0;
  border-radius: 13px;
  background: linear-gradient(135deg, #1e7bff, #00bdeb);
  box-shadow: 0 10px 22px rgba(30, 123, 255, 0.2);
  font-weight: 850;
}
</style>
