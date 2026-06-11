import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const assessments = [
  { id: 'ASS-00124', workload: 'Customer Onboarding API', product: 'ACE', cluster: 'Production', requiredVpc: 3, projected: 40, recommendation: 'Proceed', risk: 'Low', status: 'Pending', date: '09-Jun-2026' },
  { id: 'ASS-00123', workload: 'Payment Gateway', product: 'APIC', cluster: 'Production', requiredVpc: 12, projected: 49, recommendation: 'Hold', risk: 'Medium', status: 'Approved', date: '05-Jun-2026' },
  { id: 'ASS-00122', workload: 'Fraud Detection MQ', product: 'MQ', cluster: 'Non-Prod', requiredVpc: 2, projected: 15, recommendation: 'Proceed', risk: 'Low', status: 'Approved', date: '03-Jun-2026' },
  { id: 'ASS-00121', workload: 'DataSync Batch Job', product: 'ACE', cluster: 'Production', requiredVpc: 9, projected: 46, recommendation: 'Reject', risk: 'Critical', status: 'Rejected', date: '01-Jun-2026' },
  { id: 'ASS-00120', workload: 'API Gateway v2', product: 'DataPower', cluster: 'DR', requiredVpc: 3, projected: 28, recommendation: 'Proceed', risk: 'Low', status: 'Pending', date: '08-Jun-2026' },
  { id: 'ASS-00119', workload: 'KYC Verification Service', product: 'APIC', cluster: 'Production', requiredVpc: 15, projected: 52, recommendation: 'Hold', risk: 'High', status: 'Pending', date: '07-Jun-2026' },
  { id: 'ASS-00118', workload: 'Reporting Service', product: 'ACE', cluster: 'Non-Prod', requiredVpc: 4, projected: 17, recommendation: 'Proceed', risk: 'Low', status: 'Approved', date: '28-May-2026' },
]

const recommendationColor: Record<string, string> = {
  Proceed: 'bg-green-100 text-green-700',
  Hold: 'bg-amber-100 text-amber-700',
  Reject: 'bg-red-100 text-red-700',
}

const riskColor: Record<string, string> = {
  Low: 'bg-green-100 text-green-700',
  Medium: 'bg-amber-100 text-amber-700',
  High: 'bg-red-100 text-red-700',
  Critical: 'bg-red-200 text-red-800',
}

const statusColor: Record<string, string> = {
  Pending: 'bg-amber-100 text-amber-700',
  Approved: 'bg-blue-100 text-blue-700',
  Rejected: 'bg-red-100 text-red-700',
}

function Badge({ label, colorClass }: { label: string; colorClass: string }) {
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${colorClass}`}>
      {label}
    </span>
  )
}

export default function Assessments() {
  const navigate = useNavigate()
  const [clusterFilter, setClusterFilter] = useState('all')
  const [statusFilter, setStatusFilter] = useState('all')
  const [search, setSearch] = useState('')

  const filtered = assessments.filter(a => {
    const matchCluster = clusterFilter === 'all' || a.cluster.toLowerCase().includes(clusterFilter)
    const matchStatus = statusFilter === 'all' || a.status.toLowerCase() === statusFilter
    const matchSearch = a.workload.toLowerCase().includes(search.toLowerCase()) || a.id.toLowerCase().includes(search.toLowerCase())
    return matchCluster && matchStatus && matchSearch
  })

  return (
    <div className="space-y-4">

      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="text-sm font-bold text-slate-800">All Assessments</div>
        <span className="bg-slate-100 text-slate-500 text-xs font-bold px-2 py-0.5 rounded">
          {filtered.length} records
        </span>
        <div className="ml-auto flex gap-2">
          {/* Search */}
          <input
            type="text"
            placeholder="Search workload or ID..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="border border-slate-200 rounded-lg px-3 py-1.5 text-xs outline-none focus:border-blue-500 w-48"
          />
          {/* Cluster Filter */}
          <select
            value={clusterFilter}
            onChange={e => setClusterFilter(e.target.value)}
            className="border border-slate-200 rounded-lg px-3 py-1.5 text-xs outline-none focus:border-blue-500"
          >
            <option value="all">All Clusters</option>
            <option value="production">Production</option>
            <option value="non-prod">Non-Production</option>
            <option value="dr">DR</option>
          </select>
          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={e => setStatusFilter(e.target.value)}
            className="border border-slate-200 rounded-lg px-3 py-1.5 text-xs outline-none focus:border-blue-500"
          >
            <option value="all">All Status</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-slate-200">
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-slate-100">
                {['ID', 'Workload Name', 'Product', 'Cluster', 'Req. VPCs', 'Projected', 'Recommendation', 'Risk', 'Status', 'Date', 'Action'].map(h => (
                  <th key={h} className="text-left py-3 px-4 text-slate-400 font-bold uppercase tracking-wide whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={11} className="py-12 text-center text-slate-400 font-semibold">
                    No assessments found matching your filters.
                  </td>
                </tr>
              ) : (
                filtered.map(a => (
                  <tr key={a.id} className="border-b border-slate-50 hover:bg-slate-50 cursor-pointer">
                    <td className="py-3 px-4 text-blue-600 font-bold">{a.id}</td>
                    <td className="py-3 px-4 font-semibold text-slate-800">{a.workload}</td>
                    <td className="py-3 px-4 text-slate-500">{a.product}</td>
                    <td className="py-3 px-4 text-slate-500">{a.cluster}</td>
                    <td className="py-3 px-4 font-bold text-slate-800">{a.requiredVpc}</td>
                    <td className="py-3 px-4 text-slate-600">{a.projected}</td>
                    <td className="py-3 px-4"><Badge label={a.recommendation} colorClass={recommendationColor[a.recommendation]} /></td>
                    <td className="py-3 px-4"><Badge label={a.risk} colorClass={riskColor[a.risk]} /></td>
                    <td className="py-3 px-4"><Badge label={a.status} colorClass={statusColor[a.status]} /></td>
                    <td className="py-3 px-4 text-slate-400">{a.date}</td>
                    <td className="py-3 px-4">
                      <button
                        onClick={() => navigate(`/assessment/${a.id}`)}
                        className="px-3 py-1.5 border border-blue-600 text-blue-600 text-xs font-bold rounded-lg hover:bg-blue-50 transition-colors"
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}