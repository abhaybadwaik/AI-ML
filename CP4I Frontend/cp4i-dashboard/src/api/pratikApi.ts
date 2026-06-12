import axios from "axios";

// ─────────────────────────────────────────────
// BASE CONFIG
// ─────────────────────────────────────────────
const BASE_URL = "http://192.168.1.107:8000";

const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// ─────────────────────────────────────────────
// INTERCEPTOR — attach token to every request
// ─────────────────────────────────────────────
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ─────────────────────────────────────────────
// TYPES
// ─────────────────────────────────────────────

export interface WorkloadRequest {
  id?: number;
  workload_name: string;
  product: string;
  cluster: string;
  vcpus_requested: number;
  environment: string;
  justification: string;
  status?: string;
  created_at?: string;
}

export interface Assessment {
  id?: number;
  request_id: number;
  vcpus_requested: number;
  vpcs_calculated: number;
  current_usage: number;
  projected_usage: number;
  headroom: number;
  recommendation: "Proceed" | "Hold" | "Reject";
  risk_level: string;
  created_at?: string;
}

export interface ProductRatio {
  product: string;
  environment: string;
  ratio_x: number;
  ratio_y: number;
}

export interface LicenseSnapshot {
  cluster: string;
  product: string;
  licensed_vpcs: number;
  used_vpcs: number;
  available_vpcs: number;
  snapshot_date: string;
}

export interface LicenseCapacity {
  cluster: string;
  total_licensed: number;
  total_used: number;
  total_available: number;
  utilisation_percent: number;
}

// ─────────────────────────────────────────────
// 1. HEALTH CHECK
// ─────────────────────────────────────────────
export const checkHealth = async () => {
  const response = await apiClient.get("/health");
  return response.data;
};

// ─────────────────────────────────────────────
// 2. WORKLOAD REQUESTS
// ─────────────────────────────────────────────

// Get all workload requests
export const getWorkloadRequests = async () => {
  const response = await apiClient.get<WorkloadRequest[]>("/workload-requests");
  return response.data;
};

// Create a new workload request
export const createWorkloadRequest = async (payload: WorkloadRequest) => {
  const response = await apiClient.post<WorkloadRequest>("/workload-requests", payload);
  return response.data;
};

// ─────────────────────────────────────────────
// 3. PRODUCT RATIOS
// ─────────────────────────────────────────────

// Get all IBM product VPC ratios
export const getProductRatios = async () => {
  const response = await apiClient.get<ProductRatio[]>("/product-ratios");
  return response.data;
};

// ─────────────────────────────────────────────
// 4. LICENSE SNAPSHOTS
// ─────────────────────────────────────────────

// Get all license snapshots
export const getLicenseSnapshots = async () => {
  const response = await apiClient.get<LicenseSnapshot[]>("/license-snapshots");
  return response.data;
};

// ─────────────────────────────────────────────
// 5. LICENSE CAPACITY
// ─────────────────────────────────────────────

// Get license capacity per cluster
export const getLicenseCapacity = async () => {
  const response = await apiClient.get<LicenseCapacity[]>("/license-capacity");
  return response.data;
};

// ─────────────────────────────────────────────
// 6. ASSESSMENTS
// ─────────────────────────────────────────────

// Get all assessments
export const getAssessments = async () => {
  const response = await apiClient.get<Assessment[]>("/assessments");
  return response.data;
};

// Create a new assessment
export const createAssessment = async (payload: { request_id: number }) => {
  const response = await apiClient.post<Assessment>("/assessments", payload);
  return response.data;
};

// Get a single assessment by ID
export const getAssessmentById = async (assessmentId: number) => {
  const response = await apiClient.get<Assessment>(`/assessments/${assessmentId}`);
  return response.data;
};

// ─────────────────────────────────────────────
// 7. ASSESSMENT TEST (dev/debug use only)
// ─────────────────────────────────────────────

// Test assessment for a specific request
export const testAssessment = async (requestId: number) => {
  const response = await apiClient.get(`/assessment-test/${requestId}`);
  return response.data;
};