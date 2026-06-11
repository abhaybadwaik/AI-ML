import axios from 'axios'

// Base API instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor — attach token to every request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('cp4i_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor — handle auth errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('cp4i_token')
      localStorage.removeItem('cp4i_user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api


// ─── AUTH ───────────────────────────────────────────
export const authAPI = {
  login: (username: string, password: string) =>
    api.post('/auth/login', { username, password }),
}


// ─── LICENSE SNAPSHOTS (Sumith) ─────────────────────
export const licenseAPI = {
  getSnapshots: (cluster?: string) =>
    api.get('/license-snapshots', { params: { cluster } }),

  triggerIngestion: (cluster: string, sourceType: string) =>
    api.post('/ingestion-runs', { cluster, source_type: sourceType }),

  getIngestionStatus: (id: string) =>
    api.get(`/ingestion-runs/${id}`),
}


// ─── WORKLOAD REQUESTS (Pratik) ──────────────────────
export const workloadAPI = {
  submit: (data: {
    workload_name: string
    product_type: string
    estimated_cpu: number
    business_justification: string
    go_live_date: string
    cluster: string
  }) => api.post('/workload-requests', data),
}


// ─── ASSESSMENTS (Pratik) ────────────────────────────
export const assessmentAPI = {
  getAll: (params?: {
    cluster?: string
    status?: string
    from_date?: string
    to_date?: string
    page?: number
    page_size?: number
  }) => api.get('/assessments', { params }),

  getById: (id: string) =>
    api.get(`/assessments/${id}`),

  run: (requestId: string) =>
    api.post('/assessments', { request_id: requestId }),
}


// ─── APPROVALS (Prakash) ─────────────────────────────
export const approvalAPI = {
  getAll: (params?: { status?: string; cluster?: string }) =>
    api.get('/approvals', { params }),

  getById: (id: string) =>
    api.get(`/approvals/${id}`),

  submit: (assessmentId: string) =>
    api.post('/approvals', { assessment_id: assessmentId }),

  decide: (id: string, action: 'approve' | 'reject', comments: string) =>
    api.patch(`/approvals/${id}`, { action, comments }),
}


// ─── DASHBOARD (Abhay) ───────────────────────────────
export const dashboardAPI = {
  getSummary: () =>
    api.get('/dashboard'),
}


// ─── REPORTS (Abhay) ─────────────────────────────────
export const reportsAPI = {
  get: (params: {
    type: string
    cluster?: string
    from_date?: string
    to_date?: string
    format?: string
  }) => api.get('/reports', { params }),
}


// ─── USERS (Prakash) ─────────────────────────────────
export const usersAPI = {
  getAll: () => api.get('/users'),
  create: (data: { full_name: string; username: string; email: string; role: string }) =>
    api.post('/users', data),
  update: (id: number, data: Partial<{ full_name: string; role: string; status: string }>) =>
    api.patch(`/users/${id}`, data),
}