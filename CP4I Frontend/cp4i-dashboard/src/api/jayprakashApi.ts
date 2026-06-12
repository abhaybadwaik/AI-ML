import axios from "axios";

const BASE_URL = "http://192.168.1.143:8000";

const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ─── TYPES ───────────────────────────────────

export interface LoginPayload {
  username: string;
  password: string;
}

export interface SignupPayload {
  username: string;
  email: string;
  password: string;
}

// ─── AUTH ────────────────────────────────────

export const signup = async (payload: SignupPayload) => {
  const response = await apiClient.post("/auth/signup", payload);
  return response.data;
};

export const login = async (payload: LoginPayload) => {
  const response = await apiClient.post("/auth/login", payload);
  return response.data;
};

export const logout = async () => {
  const response = await apiClient.post("/auth/logout");
  return response.data;
};

export const getMe = async () => {
  const response = await apiClient.get("/auth/me");
  return response.data;
};

// ─── ADMIN ───────────────────────────────────

export const getSignupRequests = async () => {
  const response = await apiClient.get("/auth/signup-requests");
  return response.data;
};

export const approveSignupRequest = async (id: number) => {
  const response = await apiClient.post(`/auth/signup-requests/${id}/approve`);
  return response.data;
};

export const rejectSignupRequest = async (id: number, reason?: string) => {
  const response = await apiClient.post(`/auth/signup-requests/${id}/reject`, { reason });
  return response.data;
};

export const getUsers = async () => {
  const response = await apiClient.get("/auth/users");
  return response.data;
};

export const deleteUser = async (id: number) => {
  const response = await apiClient.delete(`/auth/users/${id}`);
  return response.data;
};

// ─── APPROVALS ───────────────────────────────

export const createApproval = async (assessmentId: number) => {
  const response = await apiClient.post(`/approvals/create/${assessmentId}`);
  return response.data;
};

export const getApprovals = async () => {
  const response = await apiClient.get("/approvals/");
  return response.data;
};

export const getApprovalById = async (approvalId: number) => {
  const response = await apiClient.get(`/approvals/${approvalId}`);
  return response.data;
};

export const getApprovalStatus = async (approvalId: number) => {
  const response = await apiClient.get(`/approvals/status/${approvalId}`);
  return response.data;
};

export const approvalAction = async () => {
  const response = await apiClient.get("/approvals/action");
  return response.data;
};