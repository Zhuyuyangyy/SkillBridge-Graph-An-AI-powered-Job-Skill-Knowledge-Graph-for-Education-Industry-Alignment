import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    systemName: '数融智联岗位能力图谱构建与分析系统'
  })
})
