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
  margin-bottom: 20px;
  border: 1px solid var(--border);
  border-radius: var(--radius-lg, 16px);
  padding: 12px 16px;
  background: var(--surface, #fff);
  box-shadow: var(--shadow-sm);
}
</style>
