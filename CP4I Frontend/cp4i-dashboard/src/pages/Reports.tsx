import { useState, useEffect } from 'react'
import api from '../services/api'

interface LicenseSnapshot {
  id: number
  cluster: string
  total_vpcs: number
  last_updated: string
  source: string
  products: { product_name: string; measured_quantity: number; converted_quantity: number }[]
}

interface Assessment {
  id: string
  workload_name: string
  product_type: string
  required_vpc: number
  projected_usage: number
  recommendation: string
  status: string
  assessed_at: string
}

interface Approval {
  id: string
  workload_name: string
  status: string
  decided_by?: string
  comments?: string
  decision_date?: string
  submitted_date: string
}

const recommendationColor: Record<string, string> = {
  Proceed: 'bg-green-100 text-green-700',
  Hold: 'bg-amber-100 text-amber-700',
  Reject: 'bg-red-100 text-red-700',
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

export default function Reports() {
  const [reportType, setReportType] = useState('license')
  const [cluster, setCluster] = useState('all')
  const [dateFrom, setDateFrom] = useState('2026-05-01')
  const [dateTo, setDateTo] = useState('2026-06-30')
  const [format, setFormat] = useState('screen')
  const [loading, setLoading] = useState(false)
  const [generated, setGenerated] = useState(false)

  const [snapshots, setSnapshots] = useState<LicenseSnapshot[]>([])
  const [assessments, setAssessments] = useState<Assessment[]>([])
  const [approvals, setApprovals] = useState<Approval[]>([])

  const handleGenerate = async () => {
    setLoading(true)
    setGenerated(false)
    try {
      const [snapRes, assRes, appRes] = await Promise.all([
        api.get('/license-snapshots'),
        api.get('/assessments'),
        api.get('/approvals'),
      ])
      setSnapshots(snapRes.data)
      setAssessments(assRes.data)
      setApprovals(appRes.data)
      setGenerated(true)

      if (format === 'pdf') alert('Downloading PDF...\nGET /reports?type=' + reportType + '&format=pdf')
      if (format === 'excel') alert('Downloading Excel...\nGET /reports?type=' + reportType + '&format=excel')
    } catch (err) {
      alert('Failed to generate report.')
    } finally {
      setLoading(false)
    }
  }

  const filteredSnapshots = cluster === 'all'
    ? snapshots
    : snapshots.filter(s => s.cluster === cluster)

  return (
    <div className="space-y-4">

      {/* Filter Card */}
      <div className="bg-white rounded-xl border border-slate-200 p-5">
        <div className="text-sm font-bold text-slate-800 mb-4">Report Filters</div>
        <div className="grid grid-cols-5 gap-4 items-end">
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
              value={cluster}
              onChange={e => setCluster(e.target.value)}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-xs outline-none focus:border-blue-500"
            >
              <option value="all">All Clusters</option>
              <option value="prod">Production</option>
              <option value="nonprod">Non-Production</option>
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
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Format</label>
            <select
              value={format}
              onChange={e => setFormat(e.target.value)}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-xs outline-none focus:border-blue-500"
            >
              <option value="screen">View on Screen</option>
              <option value="pdf">Download PDF</option>
              <option value="excel">Download Excel</option>
            </select>
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
            onClick={() => alert('Downloading PDF...')}
            className="px-4 py-2 border border-slate-200 text-slate-600 text-xs font-bold rounded-lg hover:bg-slate-50"
          >
            Download PDF
          </button>
          <button
            onClick={() => alert('Downloading Excel...')}
            className="px-4 py-2 border border-slate-200 text-slate-600 text-xs font-bold rounded-lg hover:bg-slate-50"
          >
            Download Excel
          </button>
          <button
            onClick={() => { setReportType('license'); setCluster('all'); setFormat('screen'); setGenerated(false) }}
            className="px-4 py-2 text-slate-400 text-xs font-bold rounded-lg hover:bg-slate-50 ml-auto"
          >
            Clear Filters
          </button>
        </div>
      </div>

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

      {/* Report Preview */}
      {generated && !loading && (
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="text-sm font-bold text-slate-800">
              {reportType === 'license' && 'License Usage Report'}
              {reportType === 'assessment' && 'Assessment Report'}
              {reportType === 'approval' && 'Approval History Report'}
              {reportType === 'consolidated' && 'Consolidated Report'}
              {' '}— {cluster === 'all' ? 'All Clusters' : cluster}
            </div>
          </div>

          {/* License Usage */}
          {(reportType === 'license' || reportType === 'consolidated') && (
            <div className="mb-6">
              {reportType === 'consolidated' && (
                <div className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-3">License Usage</div>
              )}
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-slate-100">
                      {['Cluster', 'Total VPCs', 'Limit', 'Last Updated', 'Source'].map(h => (
                        <th key={h} className="text-left py-2 px-3 text-slate-400 font-bold uppercase tracking-wide">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {filteredSnapshots.map(s => (
                      <tr key={s.id} className="border-b border-slate-50 hover:bg-slate-50">
                        <td className="py-2 px-3 font-semibold text-slate-800">{s.cluster}</td>
                        <td className="py-2 px-3 font-bold text-blue-600">{s.total_vpcs}</td>
                        <td className="py-2 px-3 text-slate-600">{s.total_vpcs}</td>
                        <td className="py-2 px-3 text-slate-600">{s.last_updated}</td>
                        <td className="py-2 px-3">
                          <span className="bg-slate-100 text-slate-500 text-xs font-bold px-2 py-0.5 rounded">{s.source}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Assessment Report */}
          {(reportType === 'assessment' || reportType === 'consolidated') && (
            <div className="mb-6">
              {reportType === 'consolidated' && (
                <div className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-3 mt-4">Assessments</div>
              )}
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-slate-100">
                      {['Date', 'Workload', 'Product', 'Req. VPC', 'Projected', 'Recommendation', 'Status'].map(h => (
                        <th key={h} className="text-left py-2 px-3 text-slate-400 font-bold uppercase tracking-wide">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {assessments.map(a => (
                      <tr key={a.id} className="border-b border-slate-50 hover:bg-slate-50">
                        <td className="py-2 px-3 text-slate-600">{a.assessed_at}</td>
                        <td className="py-2 px-3 font-semibold text-slate-800">{a.workload_name}</td>
                        <td className="py-2 px-3 text-slate-600">{a.product_type}</td>
                        <td className="py-2 px-3 font-bold text-slate-800">{a.required_vpc}</td>
                        <td className="py-2 px-3 text-slate-600">{a.projected_usage}</td>
                        <td className="py-2 px-3"><Badge label={a.recommendation} colorClass={recommendationColor[a.recommendation] || 'bg-slate-100 text-slate-600'} /></td>
                        <td className="py-2 px-3"><Badge label={statusLabel[a.status] || a.status} colorClass={statusColor[a.status] || 'bg-slate-100 text-slate-600'} /></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Approval History */}
          {(reportType === 'approval' || reportType === 'consolidated') && (
            <div>
              {reportType === 'consolidated' && (
                <div className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-3 mt-4">Approval History</div>
              )}
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-slate-100">
                      {['Date', 'Workload', 'Decision', 'Decided By', 'Comments'].map(h => (
                        <th key={h} className="text-left py-2 px-3 text-slate-400 font-bold uppercase tracking-wide">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {approvals.map(a => (
                      <tr key={a.id} className="border-b border-slate-50 hover:bg-slate-50">
                        <td className="py-2 px-3 text-slate-600">{a.decision_date || a.submitted_date}</td>
                        <td className="py-2 px-3 font-semibold text-slate-800">{a.workload_name}</td>
                        <td className="py-2 px-3">
                          <Badge
                            label={statusLabel[a.status] || a.status}
                            colorClass={statusColor[a.status] || 'bg-slate-100 text-slate-600'}
                          />
                        </td>
                        <td className="py-2 px-3 text-slate-600">{a.decided_by || '—'}</td>
                        <td className="py-2 px-3 text-slate-500">{a.comments || '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}