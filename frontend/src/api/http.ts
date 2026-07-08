import axios from 'axios'

export const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '',
  timeout: 15000
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const api = {
  register: (payload: unknown) => http.post('/api/auth/register', payload).then((res) => res.data),
  captcha: () => http.get('/api/auth/captcha').then((res) => res.data),
  login: (payload: unknown) => http.post('/api/auth/login', payload).then((res) => res.data),
  logout: () => http.post('/api/auth/logout').then((res) => res.data),
  me: () => http.get('/api/auth/me').then((res) => res.data),
  changePassword: (payload: unknown) => http.post('/api/auth/change-password', payload).then((res) => res.data),
  updateAccount: (payload: unknown) => http.put('/api/account', payload).then((res) => res.data),
  myProfile: () => http.get('/api/profile/me').then((res) => res.data),
  updateMyProfile: (payload: unknown) => http.put('/api/profile/me', payload).then((res) => res.data),
  hrCandidates: () => http.get('/api/hr/candidates').then((res) => res.data),
  overview: () => http.get('/api/overview/summary').then((res) => res.data),
  datasets: () => http.get('/api/datasets').then((res) => res.data),
  parseJd: (text: string) => http.post('/api/jd/parse', { text }).then((res) => res.data),
  jobs: () => http.get('/api/jobs').then((res) => res.data),
  emergingJobs: () => http.get('/api/emerging-jobs').then((res) => res.data),
  jobEvolution: (id: number) => http.get(`/api/job-evolution/${id}`).then((res) => res.data),
  skillGraph: () => http.get('/api/skill-graph').then((res) => res.data),
  graphFull: (params?: { keyword?: string; community?: number; limit?: number }) =>
    http.get('/api/graph/full', { params }).then((res) => res.data),
  graphStats: () => http.get('/api/graph/stats').then((res) => res.data),
  graphCommunities: () => http.get('/api/graph/communities').then((res) => res.data),
  graphPath: (from_job: number, to_job: number) =>
    http.get('/api/graph/path', { params: { from_job, to_job } }).then((res) => res.data),
  graphSearch: (keyword: string) => http.get('/api/graph/search', { params: { keyword } }).then((res) => res.data),
  evolutionTimeline: () => http.get('/api/evolution/timeline').then((res) => res.data),
  evolutionHotspot: () => http.get('/api/evolution/hotspot').then((res) => res.data),
  evolutionCompare: () => http.get('/api/evolution/compare').then((res) => res.data),
  evolutionVersionCompare: () => http.get('/api/evolution/version-compare').then((res) => res.data),
  graphEvidence: (node_type: 'job' | 'skill', node_id: number) =>
    http.get('/api/graph/evidence', { params: { node_type, node_id } }).then((res) => res.data),
  parseResume: (text: string) => http.post('/api/resume/parse', { text }).then((res) => res.data),
  matchAnalysis: (payload: unknown) => http.post('/api/match-analysis', payload).then((res) => res.data),
  learningPath: (id: number) => http.get(`/api/learning-path/${id}`).then((res) => res.data),
  reviewTasks: () => http.get('/api/review-tasks').then((res) => res.data),
  approveTask: (id: number) => http.post(`/api/review-tasks/${id}/approve`).then((res) => res.data),
  rejectTask: (id: number) => http.post(`/api/review-tasks/${id}/reject`).then((res) => res.data),
  evaluation: () => http.get('/api/evaluation/metrics').then((res) => res.data),
  resumes: () => http.get('/api/resumes').then((res) => res.data),
  aiStatus: () => http.get('/api/ai/status').then((res) => res.data),
  aiAnalyze: (task_type: string, payload: Record<string, unknown>) => http.post('/api/ai/analyze', { task_type, payload }).then((res) => res.data),
  digitalInterview: (payload: { job_name: string; resume_summary?: string; candidate_answer?: string; stage?: string }) =>
    http.post('/api/digital-interviewer/interview', payload).then((res) => res.data)
}
