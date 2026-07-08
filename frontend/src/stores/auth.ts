import { defineStore } from 'pinia'
import { api } from '@/api/http'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('auth_token') || '',
    user: JSON.parse(localStorage.getItem('auth_user') || 'null') as any
  }),
  getters: {
    isLoggedIn: (state) => Boolean(state.token && state.user),
    role: (state) => state.user?.role || ''
  },
  actions: {
    setSession(token: string, user: any) {
      this.token = token
      this.user = user
      localStorage.setItem('auth_token', token)
      localStorage.setItem('auth_user', JSON.stringify(user))
    },
    async login(username: string, password: string) {
      const data = await api.login({ username, password })
      this.setSession(data.token, data.user)
      return data.user
    },
    async register(payload: any) {
      const data = await api.register(payload)
      this.setSession(data.token, data.user)
      return data.user
    },
    async refreshMe() {
      if (!this.token) return
      this.user = await api.me()
      localStorage.setItem('auth_user', JSON.stringify(this.user))
    },
    async logout() {
      try {
        if (this.token) await api.logout()
      } finally {
        this.token = ''
        this.user = null
        localStorage.removeItem('auth_token')
        localStorage.removeItem('auth_user')
      }
    }
  }
})
