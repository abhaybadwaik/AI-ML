export const clusterData = [
  {
    name: 'Production',
    key: 'prod',
    totalVpcs: 37,
    limitVpcs: 50,
    lastUpdated: '01-Jun-2026 10:03',
    products: [
      { name: 'ACE', vpcs: 12 },
      { name: 'APIC', vpcs: 18 },
      { name: 'MQ', vpcs: 1 },
      { name: 'DataPower', vpcs: 6 },
    ],
  },
  {
    name: 'Non-Production',
    key: 'nonprod',
    totalVpcs: 13,
    limitVpcs: 50,
    lastUpdated: '01-Jun-2026 10:05',
    products: [
      { name: 'ACE', vpcs: 6 },
      { name: 'APIC', vpcs: 3 },
      { name: 'MQ', vpcs: 2 },
      { name: 'DataPower', vpcs: 1 },
    ],
  },
  {
    name: 'DR',
    key: 'dr',
    totalVpcs: 25,
    limitVpcs: 50,
    lastUpdated: '01-Jun-2026 10:08',
    products: [
      { name: 'APIC', vpcs: 18 },
      { name: 'MQ', vpcs: 2 },
      { name: 'DataPower', vpcs: 6 },
    ],
  },
]

export const recentAssessments = [
  { id: 'ASS-001', workload: 'Customer Onboarding API', product: 'ACE', requiredVpc: 3, recommendation: 'Proceed', risk: 'Low', status: 'Pending', date: '09-Jun-2026' },
  { id: 'ASS-002', workload: 'Payment Gateway', product: 'APIC', requiredVpc: 12, recommendation: 'Hold', risk: 'Medium', status: 'Approved', date: '05-Jun-2026' },
  { id: 'ASS-003', workload: 'Fraud Detection MQ', product: 'MQ', requiredVpc: 2, recommendation: 'Proceed', risk: 'Low', status: 'Approved', date: '03-Jun-2026' },
  { id: 'ASS-004', workload: 'DataSync Batch Job', product: 'ACE', requiredVpc: 9, recommendation: 'Reject', risk: 'Critical', status: 'Rejected', date: '01-Jun-2026' },
  { id: 'ASS-005', workload: 'API Gateway v2', product: 'DataPower', requiredVpc: 3, recommendation: 'Proceed', risk: 'Low', status: 'Pending', date: '08-Jun-2026' },
]

export const pendingApprovals = [
  { id: 'APP-001', workload: 'Customer Onboarding API', risk: 'Low', recommendation: 'Proceed' },
  { id: 'APP-002', workload: 'API Gateway v2', risk: 'Low', recommendation: 'Proceed' },
  { id: 'APP-003', workload: 'KYC Verification Service', risk: 'High', recommendation: 'Hold' },
]