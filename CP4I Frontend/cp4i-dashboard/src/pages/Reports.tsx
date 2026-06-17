import { useState } from 'react'
import { licenseAPI, assessmentAPI, approvalAPI } from '../services/api'

interface Snapshot {
  id: number
  cluster: string
  product_name: string
  converted_quantity: number
  collected_at: string
}

interface Assessment {
  id: number
  request_id: number
  current_usage: number
  required_vpc: number
  projected_usage: number
  available_headroom: number
  recommendation: string
  risk_level: string
  assessed_at: string
}

interface Approval {
  id: number
  assessment_id: number
  status: string
  requested_by: string
  requested_at: string
  reviewed_by: string | null
  reviewed_at: string | null
  comments: string | null
}

const recommendationColor: Record<string, string> = {
  Proceed: 'bg-green-100 text-green-700',
  Hold: 'bg-amber-100 text-amber-700',
  Reject: 'bg-red-100 text-red-700',
}

const statusColor: Record<string, string> = {
  pending: 'bg-amber-100 text-amber-700',
  approved: 'bg-green-100 text-green-700',
  rejected: 'bg-red-100 text-red-700',
}

const riskColor: Record<string, string> = {
  low: 'bg-green-100 text-green-700',
  medium: 'bg-amber-100 text-amber-700',
  high: 'bg-red-100 text-red-700',
  critical: 'bg-red-200 text-red-800',
}

function Badge({ label, colorClass }: { label: string; colorClass: string }) {
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${colorClass}`}>
      {label}
    </span>
  )
}

export default function Reports() {
  const [reportType, setReportType] = useState('license')
  const [clusterFilter, setClusterFilter] = useState('all')
  const [dateFrom, setDateFrom] = useState('2026-05-01')
  const [dateTo, setDateTo] = useState('2026-06-30')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [generated, setGenerated] = useState(false)

  const [snapshots, setSnapshots] = useState<Snapshot[]>([])
  const [assessments, setAssessments] = useState<Assessment[]>([])
  const [approvals, setApprovals] = useState<Approval[]>([])

  const handleGenerate = async () => {
    setLoading(true)
    setGenerated(false)
    setError('')
    try {
      const [snapRes, assRes, appRes] = await Promise.all([
        licenseAPI.getSnapshots(),
        assessmentAPI.getAll(),
        approvalAPI.getAll(),
      ])

      const snapData = Array.isArray(snapRes.data) ? snapRes.data : []
      const assData = Array.isArray(assRes.data) ? assRes.data : assRes.data.items ?? []
      const appData = Array.isArray(appRes.data) ? appRes.data : appRes.data.items ?? []

      setSnapshots(snapData)
      setAssessments(assData)
      setApprovals(appData)
      setGenerated(true)
    } catch (err) {
      setError('Failed to generate report. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleClear = () => {
    setReportType('license')
    setClusterFilter('all')
    setDateFrom('2026-05-01')
    setDateTo('2026-06-30')
    setGenerated(false)
    setError('')
  }

  // Filter snapshots by cluster
  const filteredSnapshots = clusterFilter === 'all'
    ? snapshots
    : snapshots.filter(s => s.cluster === clusterFilter)

  // Group snapshots by cluster for license report
  const groupedSnapshots = filteredSnapshots.reduce((acc, s) => {
    if (!acc[s.cluster]) acc[s.cluster] = []
    acc[s.cluster].push(s)
    return acc
  }, {} as Record<string, Snapshot[]>)

  // Filter assessments by date
  const filteredAssessments = assessments.filter(a => {
    const date = a.assessed_at?.substring(0, 10)
    return (!dateFrom || date >= dateFrom) && (!dateTo || date <= dateTo)
  })

  // Filter approvals by date
  const filteredApprovals = approvals.filter(a => {
    const date = a.requested_at?.substring(0, 10)
    return (!dateFrom || date >= dateFrom) && (!dateTo || date <= dateTo)
  })

  return (
    <div className="space-y-4">

      {/* Filter Card */}
      <div className="bg-white rounded-xl border border-slate-200 p-5">
        <div className="text-sm font-bold text-slate-800 mb-4">Report Filters</div>
        <div className="grid grid-cols-4 gap-4 items-end">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Report Type</label>
            <select
              value={reportType}
              onChange={e => { setReportType(e.target.value); setGenerated(false) }}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-xs outline-none focus:border-blue-500"
            >
              <option value="license">License Usage</option>
              <option value="assessment">Assessment Report</option>
              <option value="approval">Approval History</option>
              <option value="consolidated">Consolidated</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Cluster</label>
            <select
              value={clusterFilter}
              onChange={e => setClusterFilter(e.target.value)}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-xs outline-none focus:border-blue-500"
            >
              <option value="all">All Clusters</option>
              <option value="prod">Production</option>
              <option value="non-prod">Non-Production</option>
              <option value="dr">DR</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Date From</label>
            <input
              type="date" value={dateFrom}
              onChange={e => setDateFrom(e.target.value)}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-xs outline-none focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Date To</label>
            <input
              type="date" value={dateTo}
              onChange={e => setDateTo(e.target.value)}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-xs outline-none focus:border-blue-500"
            />
          </div>
        </div>
        <div className="flex gap-2 mt-4">
          <button
            onClick={handleGenerate}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white text-xs font-bold rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Generating...' : 'Generate Report'}
          </button>
          <button
            onClick={handleClear}
            className="px-4 py-2 text-slate-400 text-xs font-bold rounded-lg hover:bg-slate-50 ml-auto"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-600 font-semibold">
          {error}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
          <div className="flex justify-center gap-1 mb-2">
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
          <div className="text-xs text-slate-400">Generating report...</div>
        </div>
      )}

      {/* Report Output */}
      {generated && !loading && (
        <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-6">

          <div className="text-sm font-bold text-slate-800">
            {reportType === 'license' && 'License Usage Report'}
            {reportType === 'assessment' && 'Assessment Report'}
            {reportType === 'approval' && 'Approval History'}
            {reportType === 'consolidated' && 'Consolidated Report'}
            {' '}— {clusterFilter === 'all' ? 'All Clusters' : clusterFilter} · {dateFrom} to {dateTo}
          </div>

          {/* LICENSE */}
          {(reportType === 'license' || reportType === 'consolidated') && (
            <div>
              {reportType === 'consolidated' && (
                <div className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-2">License Usage</div>
              )}
              {Object.keys(groupedSnapshots).length === 0 ? (
                <div className="text-xs text-slate-400 py-4">No license data found.</div>
              ) : (
                Object.entries(groupedSnapshots).map(([clusterKey, products]) => (
                  <div key={clusterKey} className="mb-4">
                    <div className="text-xs font-bold text-slate-600 mb-2 capitalize">{clusterKey}</div>
                    <table className="w-full text-xs">
                      <thead>
                        <tr className="border-b border-slate-100">
                          {['Product', 'VPCs Used', 'Collected At'].map(h => (
                            <th key={h} className="text-left py-2 px-3 text-slate-400 font-bold uppercase tracking-wide">{h}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {products.map(p => (
                          <tr key={p.id} className="border-b border-slate-50 hover:bg-slate-50">
                            <td className="py-2 px-3 font-semibold text-slate-800">{p.product_name}</td>
                            <td className="py-2 px-3 font-bold text-blue-600">{p.converted_quantity}</td>
                            <td className="py-2 px-3 text-slate-500">
                              {new Date(p.collected_at).toLocaleDateString()}
                            </td>
                          </tr>
                        ))}
                        <tr className="bg-slate-50 font-bold">
                          <td className="py-2 px-3 text-slate-800">Total</td>
                          <td className="py-2 px-3 text-slate-800">
                            {products.reduce((s, p) => s + p.converted_quantity, 0)}
                          </td>
                          <td />
                        </tr>
                      </tbody>
                    </table>
                  </div>
                ))
              )}
            </div>
          )}

          {/* ASSESSMENTS */}
          {(reportType === 'assessment' || reportType === 'consolidated') && (
            <div>
              {reportType === 'consolidated' && (
                <div className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-2 mt-2">Assessments</div>
              )}
              {filteredAssessments.length === 0 ? (
                <div className="text-xs text-slate-400 py-4">No assessments found in date range.</div>
              ) : (
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-slate-100">
                      {['ID', 'Request ID', 'Req. VPCs', 'Current', 'Projected', 'Headroom', 'Recommendation', 'Risk', 'Date'].map(h => (
                        <th key={h} className="text-left py-2 px-3 text-slate-400 font-bold uppercase tracking-wide whitespace-nowrap">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {filteredAssessments.map(a => (
                      <tr key={a.id} className="border-b border-slate-50 hover:bg-slate-50">
                        <td className="py-2 px-3 text-blue-600 font-bold">{a.id}</td>
                        <td className="py-2 px-3 text-slate-500">#{a.request_id}</td>
                        <td className="py-2 px-3 font-bold text-slate-800">{a.required_vpc}</td>
                        <td className="py-2 px-3 text-slate-600">{a.current_usage}</td>
                        <td className="py-2 px-3 text-slate-600">{a.projected_usage}</td>
                        <td className={`py-2 px-3 font-bold ${a.available_headroom < 0 ? 'text-red-600' : 'text-green-600'}`}>
                          {a.available_headroom}
                        </td>
                        <td className="py-2 px-3">
                          <Badge label={a.recommendation} colorClass={recommendationColor[a.recommendation] || 'bg-slate-100 text-slate-600'} />
                        </td>
                        <td className="py-2 px-3">
                          <Badge label={a.risk_level} colorClass={riskColor[a.risk_level?.toLowerCase()] || 'bg-slate-100 text-slate-600'} />
                        </td>
                        <td className="py-2 px-3 text-slate-400">
                          {new Date(a.assessed_at).toLocaleDateString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          )}

          {/* APPROVALS */}
          {(reportType === 'approval' || reportType === 'consolidated') && (
            <div>
              {reportType === 'consolidated' && (
                <div className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-2 mt-2">Approval History</div>
              )}
              {filteredApprovals.length === 0 ? (
                <div className="text-xs text-slate-400 py-4">No approvals found in date range.</div>
              ) : (
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-slate-100">
                      {['ID', 'Assessment ID', 'Requested By', 'Status', 'Reviewed By', 'Comments', 'Date'].map(h => (
                        <th key={h} className="text-left py-2 px-3 text-slate-400 font-bold uppercase tracking-wide whitespace-nowrap">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {filteredApprovals.map(a => (
                      <tr key={a.id} className="border-b border-slate-50 hover:bg-slate-50">
                        <td className="py-2 px-3 text-blue-600 font-bold">{a.id}</td>
                        <td className="py-2 px-3 text-slate-500">#{a.assessment_id}</td>
                        <td className="py-2 px-3 font-semibold text-slate-800">{a.requested_by}</td>
                        <td className="py-2 px-3">
                          <Badge
                            label={a.status.charAt(0).toUpperCase() + a.status.slice(1)}
                            colorClass={statusColor[a.status] || 'bg-slate-100 text-slate-600'}
                          />
                        </td>
                        <td className="py-2 px-3 text-slate-500">{a.reviewed_by ?? '—'}</td>
                        <td className="py-2 px-3 text-slate-500">{a.comments ?? '—'}</td>
                        <td className="py-2 px-3 text-slate-400">
                          {new Date(a.requested_at).toLocaleDateString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          )}

        </div>
      )}
    </div>
  )
}