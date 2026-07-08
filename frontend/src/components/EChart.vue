<template>
  <div ref="chartRef" class="chart"></div>
</template>

<script setup lang="ts">
import * as echarts from 'echarts'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps<{ option: any }>()
const chartRef = ref<HTMLDivElement>()
let chart: echarts.ECharts | undefined

function render() {
  if (!chartRef.value) return
  try {
    if (!chart || chart.isDisposed()) {
      chart = echarts.init(chartRef.value)
    }
    chart.setOption(props.option || {}, true)
  } catch (error) {
    console.warn('EChart render failed', error)
  }
}

function resize() {
  chart?.resize()
}

onMounted(() => {
  render()
  window.addEventListener('resize', resize)
})

watch(() => props.option, render, { deep: true })

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  if (chart && !chart.isDisposed()) {
    chart.dispose()
  }
  chart = undefined
})
</script>
