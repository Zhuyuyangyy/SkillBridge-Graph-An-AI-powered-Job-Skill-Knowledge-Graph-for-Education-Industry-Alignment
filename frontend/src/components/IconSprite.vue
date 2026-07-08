<template>
  <span
    class="sprite-icon"
    :class="[`sprite-${name}`, className]"
    :style="{ width: `${size}px`, height: `${size}px` }"
  />
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    name: 'profile' | 'progress' | 'certificate' | 'folder' | 'target' | 'chart' | 'education' | 'shield' | 'setting'
    size?: number
    className?: string
  }>(),
  {
    size: 48,
    className: ''
  }
)
</script>

<style scoped>
.sprite-icon {
  --sprite-shift-x: 0%;
  --sprite-shift-y: 0%;
  --sprite-scale: 1;
  display: inline-block;
  flex: 0 0 auto;
  background-image: url('@/assets/images/profile-icon-sheet.png');
  background-repeat: no-repeat;
  background-size: 300% 300%;
  border-radius: 18px;
  overflow: hidden;
  filter: drop-shadow(0 10px 18px rgba(30, 123, 255, 0.22));
  transform: translate(var(--sprite-shift-x), var(--sprite-shift-y)) scale(var(--sprite-scale));
  transform-origin: center;
}

.sprite-profile {
  --sprite-shift-x: -11%;
  --sprite-shift-y: -14%;
  background-position: 0% 0%;
}

.sprite-progress {
  --sprite-shift-x: 1%;
  --sprite-shift-y: -13%;
  background-position: 50% 0%;
}

.sprite-certificate {
  --sprite-shift-x: 9%;
  --sprite-shift-y: -14%;
  background-position: 100% 0%;
}

.sprite-folder {
  --sprite-shift-x: -11%;
  --sprite-shift-y: -6%;
  background-position: 0% 50%;
}

.sprite-target {
  --sprite-shift-x: -2%;
  --sprite-shift-y: -4%;
  background-position: 50% 50%;
}

.sprite-chart {
  --sprite-shift-x: 8%;
  --sprite-shift-y: -1%;
  background-position: 100% 50%;
}

.sprite-education {
  --sprite-shift-x: -7%;
  --sprite-shift-y: 10%;
  background-position: 0% 100%;
}

.sprite-shield {
  --sprite-shift-x: 1%;
  --sprite-shift-y: 10%;
  background-position: 50% 100%;
}

.sprite-setting {
  --sprite-shift-x: 8%;
  --sprite-shift-y: 9%;
  background-position: 100% 100%;
}
</style>
