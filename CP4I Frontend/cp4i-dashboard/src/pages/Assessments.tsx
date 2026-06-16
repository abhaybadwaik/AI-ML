import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'

interface Assessment {
  id: string
  workload_name: string
  product_type: string
  cluster: string
  required_vpc: number
  projected_usage: number
  recommendation: string
  risk_level: string
  status: string
  assessed_at: string
}

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
  pending_approval: 'bg-amber-100 text-amber-700',
  approved: 'bg-blue-100 text-blue-700',
  rejected: 'bg-red-100 text-red-700',
}

const statusLabel: Record<string, string> = {
  pending_approval: 'Pending',
  approved: 'Approved',
  rejected: 'Rejected',
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
  const [assessments, setAssessments] = useState<Assessment[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [clusterFilter, setClusterFilter] = useState('all')
  const [statusFilter, setStatusFilter] = useState('all')
  const [search, setSearch] = useState('')

  useEffect(() => {
    fetchAssessments()
  }, [])

  const fetchAssessments = async () => {
    try {
      setLoading(true)
      setError('')
      const response = await api.get('/assessments')
      setAssessments(response.data)
    } catch (err) {
      setError('Failed to load assessments. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const filtered = assessments.filter(a => {
    const matchCluster = clusterFilter === 'all' || a.cluster === clusterFilter
    const matchStatus = statusFilter === 'all' || a.status === statusFilter
    const matchSearch = a.workload_name.toLowerCase().includes(search.toLowerCase()) ||
      a.id.toLowerCase().includes(search.toLowerCase())
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
          <input
            type="text"
            placeholder="Search workload or ID..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="border border-slate-200 rounded-lg px-3 py-1.5 text-xs outline-none focus:border-blue-500 w-48"
          />
          <select
            value={clusterFilter}
            onChange={e => setClusterFilter(e.target.value)}
            className="border border-slate-200 rounded-lg px-3 py-1.5 text-xs outline-none focus:border-blue-500"
          >
            <option value="all">All Clusters</option>
            <option value="prod">Production</option>
            <option value="nonprod">Non-Production</option>
            <option value="dr">DR</option>
          </select>
          <select
            value={statusFilter}
            onChange={e => setStatusFilter(e.target.value)}
            className="border border-slate-200 rounded-lg px-3 py-1.5 text-xs outline-none focus:border-blue-500"
          >
            <option value="all">All Status</option>
            <option value="pending_approval">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
          <button
            onClick={fetchAssessments}
            className="px-3 py-1.5 bg-blue-600 text-white text-xs font-bold rounded-lg hover:bg-blue-700"
          >
            ↺ Refresh
          </button>
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
          <div className="flex justify-center gap-1 mb-3">
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
          <div className="text-xs text-slate-400">Loading assessments...</div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-600 font-semibold">
          {error}
          <button onClick={fetchAssessments} className="ml-3 underline text-red-700">Retry</button>
        </div>
      )}

      {/* Table */}
      {!loading && !error && (
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
                      No assessments found.
                    </td>
                  </tr>
                ) : (
                  filtered.map(a => (
                    <tr key={a.id} className="border-b border-slate-50 hover:bg-slate-50">
                      <td className="py-3 px-4 text-blue-600 font-bold">{a.id}</td>
                      <td className="py-3 px-4 font-semibold text-slate-800">{a.workload_name}</td>
                      <td className="py-3 px-4 text-slate-500">{a.product_type}</td>
                      <td className="py-3 px-4 text-slate-500">{a.cluster}</td>
                      <td className="py-3 px-4 font-bold text-slate-800">{a.required_vpc}</td>
                      <td className="py-3 px-4 text-slate-600">{a.projected_usage}</td>
                      <td className="py-3 px-4"><Badge label={a.recommendation} colorClass={recommendationColor[a.recommendation] || 'bg-slate-100 text-slate-600'} /></td>
                      <td className="py-3 px-4"><Badge label={a.risk_level} colorClass={riskColor[a.risk_level] || 'bg-slate-100 text-slate-600'} /></td>
                      <td className="py-3 px-4"><Badge label={statusLabel[a.status] || a.status} colorClass={statusColor[a.status] || 'bg-slate-100 text-slate-600'} /></td>
                      <td className="py-3 px-4 text-slate-400">{a.assessed_at}</td>
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
      )}
    </div>
  )
}