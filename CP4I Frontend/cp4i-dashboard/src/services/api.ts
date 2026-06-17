import axios from 'axios'

// ─── JAY'S INSTANCE (auth + approvals) ──────────────
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://192.168.1.143:8000',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('cp4i_token')
    if (token) config.headers.Authorization = `Bearer ${token}`
    return config
  },
  (error) => Promise.reject(error)
)

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


// ─── PRATIK'S INSTANCE (assessments + workload) ─────
const pratikApi = axios.create({
  baseURL: import.meta.env.VITE_PRATIK_API_BASE_URL || 'http://192.168.1.107:8000',
  headers: { 'Content-Type': 'application/json' },
})

pratikApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('cp4i_token')
    if (token) config.headers.Authorization = `Bearer ${token}`
    return config
  },
  (error) => Promise.reject(error)
)

pratikApi.interceptors.response.use(
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


// ─── AUTH (Jay) ──────────────────────────────────────
export const authAPI = {
  login: (username: string, password: string) => {
    const form = new URLSearchParams()
    form.append('username', username)
    form.append('password', password)
    return api.post('/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
  },
  signup: (username: string, email: string, full_name: string, password: string) =>
    api.post('/auth/signup', { username, email, full_name, password }),
  logout: () => api.post('/auth/logout'),
  getMe: () => api.get('/auth/me'),
}


// ─── ADMIN (Jay) ─────────────────────────────────────
export const adminAPI = {
  getSignupRequests: (status: string = 'pending') =>
    api.get(`/auth/signup-requests?status=${status}`),
  approveSignupRequest: (id: number, role: string) =>
    api.post(`/auth/signup-requests/${id}/approve`, { role }),
  rejectSignupRequest: (id: number, reason?: string) =>
    api.post(`/auth/signup-requests/${id}/reject`, { reason }),
  getUsers: () => api.get('/auth/users'),
  deleteUser: (id: number) => api.delete(`/auth/users/${id}`),
}


// ─── APPROVALS (Jay) ─────────────────────────────────
export const approvalAPI = {
  getAll: () => api.get('/approvals/'),
  getById: (id: number) => api.get(`/approvals/${id}`),
  getStatus: (id: number) => api.get(`/approvals/status/${id}`),
  create: (assessmentId: number, requestedBy: string) =>
    api.post(`/approvals/create/${assessmentId}`, { requested_by: requestedBy }),
  approve: (id: number) =>
    api.patch(`/approvals/${id}`, { status: 'approved' }),
  reject: (id: number, comments: string) =>
    api.patch(`/approvals/${id}`, { status: 'rejected', comments }),
}


// ─── WORKLOAD REQUESTS (Pratik) ──────────────────────
export const workloadAPI = {
  getAll: () => pratikApi.get('/workload-requests'),
  getById: (id: string) => pratikApi.get(`/workload-requests/${id}`),
  submit: (data: {
    workload_name: string
    product_type: string
    estimated_cpu: number
    business_justification: string
    requested_by: string
    go_live_date: string
    cluster: string
  }) => pratikApi.post('/workload-requests', data),
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
  }) => pratikApi.get('/assessments', { params }),
  getById: (id: string) => pratikApi.get(`/assessments/${id}`),
  // run() removed — POST /workload-requests handles everything now
}


// ─── LICENSE (Pratik) ────────────────────────────────
export const licenseAPI = {
  getSnapshots: () => pratikApi.get('/license-snapshots'),
  getCapacity: () => pratikApi.get('/license-capacity'),
  getProductRatios: () => pratikApi.get('/product-ratios'),
}


// ─── DASHBOARD (Abhay) ───────────────────────────────
export const dashboardAPI = {
  getSummary: () => api.get('/dashboard'),
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


// ─── USERS (Jay) ─────────────────────────────────────
export const usersAPI = {
  getAll: () => api.get('/auth/users'),
  delete: (id: number) => api.delete(`/auth/users/${id}`),
}