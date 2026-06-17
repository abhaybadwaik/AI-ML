import { useState, useEffect } from 'react'
import { approvalAPI } from '../services/api'

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

function Badge({ label, colorClass }: { label: string; colorClass: string }) {
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${colorClass}`}>
      {label}
    </span>
  )
}

const statusColor: Record<string, string> = {
  pending: 'bg-amber-100 text-amber-700',
  approved: 'bg-green-100 text-green-700',
  rejected: 'bg-red-100 text-red-700',
}

export default function Approvals() {
  const [approvals, setApprovals] = useState<Approval[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState('pending')
  const [selectedApproval, setSelectedApproval] = useState<Approval | null>(null)
  const [comments, setComments] = useState('')
  const [actionLoading, setActionLoading] = useState(false)
  const [actionError, setActionError] = useState('')

  useEffect(() => {
    fetchApprovals()
  }, [])

  const fetchApprovals = async () => {
    try {
      setLoading(true)
      setError('')
      const response = await approvalAPI.getAll()
      const data = Array.isArray(response.data)
        ? response.data
        : response.data.items ?? response.data.results ?? []
      setApprovals(data)
    } catch (err) {
      setError('Failed to load approvals.')
    } finally {
      setLoading(false)
    }
  }

  const handleAction = async (action: 'approve' | 'reject') => {
    if (!selectedApproval) return
    setActionLoading(true)
    setActionError('')
    try {
      if (action === 'approve') {
        await approvalAPI.approve(selectedApproval.id)
      } else {
        await approvalAPI.reject(selectedApproval.id, comments)
      }
      await fetchApprovals()
      setSelectedApproval(null)
      setComments('')
    } catch (err: any) {
      setActionError(err.response?.data?.detail || 'Action failed. Please try again.')
    } finally {
      setActionLoading(false)
    }
  }

  const pending = approvals.filter(a => a.status === 'pending')
  const approved = approvals.filter(a => a.status === 'approved')
  const rejected = approvals.filter(a => a.status === 'rejected')

  const tabs = [
    { key: 'pending', label: `Pending (${pending.length})` },
    { key: 'approved', label: `Approved (${approved.length})` },
    { key: 'rejected', label: `Rejected (${rejected.length})` },
    { key: 'all', label: `All (${approvals.length})` },
  ]

  const activeList = activeTab === 'pending' ? pending
    : activeTab === 'approved' ? approved
    : activeTab === 'rejected' ? rejected
    : approvals

  return (
    <div className="space-y-4">

      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="text-sm font-bold text-slate-800">Approval Queue</div>
        <span className="bg-amber-100 text-amber-700 text-xs font-bold px-2 py-0.5 rounded-full">
          {pending.length} Pending
        </span>
        <div className="ml-auto flex gap-2">
          <button
            onClick={fetchApprovals}
            className="px-3 py-1.5 text-xs font-semibold border border-slate-200 text-slate-600 rounded-lg hover:bg-slate-50"
          >
            ↺ Refresh
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-slate-200">
        {tabs.map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2 text-xs font-semibold border-b-2 transition-colors -mb-px
              ${activeTab === tab.key
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-slate-400 hover:text-slate-600'
              }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-600 font-semibold">
          {error}
          <button onClick={fetchApprovals} className="ml-3 underline">Retry</button>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
          <div className="flex justify-center gap-1">
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
        </div>
      )}

      {/* Table */}
      {!loading && !error && (
        <div className="bg-white rounded-xl border border-slate-200">
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-slate-100">
                  {['ID', 'Assessment ID', 'Requested By', 'Status', 'Requested At', 'Reviewed By', 'Reviewed At', 'Action'].map(h => (
                    <th key={h} className="text-left py-3 px-4 text-slate-400 font-bold uppercase tracking-wide whitespace-nowrap">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {activeList.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="py-12 text-center text-slate-400 font-semibold">
                      No records found.
                    </td>
                  </tr>
                ) : (
                  activeList.map(a => (
                    <tr key={a.id} className="border-b border-slate-50 hover:bg-slate-50">
                      <td className="py-3 px-4 text-blue-600 font-bold">{a.id}</td>
                      <td className="py-3 px-4 text-slate-500">#{a.assessment_id}</td>
                      <td className="py-3 px-4 font-semibold text-slate-800">{a.requested_by}</td>
                      <td className="py-3 px-4">
                        <Badge
                          label={a.status.charAt(0).toUpperCase() + a.status.slice(1)}
                          colorClass={statusColor[a.status] || 'bg-slate-100 text-slate-600'}
                        />
                      </td>
                      <td className="py-3 px-4 text-slate-400">
                        {new Date(a.requested_at).toLocaleDateString()}
                      </td>
                      <td className="py-3 px-4 text-slate-500">{a.reviewed_by ?? '—'}</td>
                      <td className="py-3 px-4 text-slate-400">
                        {a.reviewed_at ? new Date(a.reviewed_at).toLocaleDateString() : '—'}
                      </td>
                      <td className="py-3 px-4">
                        {a.status === 'pending' ? (
                          <button
                            onClick={() => { setSelectedApproval(a); setComments(''); setActionError('') }}
                            className="px-3 py-1.5 bg-blue-600 text-white text-xs font-bold rounded-lg hover:bg-blue-700"
                          >
                            Review
                          </button>
                        ) : (
                          <span className={`text-xs font-bold ${a.status === 'approved' ? 'text-green-600' : 'text-red-600'}`}>
                            {a.status === 'approved' ? '✓ Approved' : '✗ Rejected'}
                          </span>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Slide Panel */}
      {selectedApproval && (
        <>
          <div className="fixed inset-0 bg-black/20 z-40" onClick={() => setSelectedApproval(null)} />
          <div className="fixed right-0 top-0 bottom-0 w-96 bg-white border-l border-slate-200 z-50 overflow-y-auto shadow-2xl">
            <div className="p-6 space-y-4">
              <div className="flex items-center justify-between">
                <div className="text-sm font-bold text-slate-800">Review Approval</div>
                <button onClick={() => setSelectedApproval(null)} className="text-slate-400 hover:text-slate-600 font-bold text-lg">✕</button>
              </div>

              <div className="text-xs text-slate-400">
                Approval #{selectedApproval.id} · Assessment #{selectedApproval.assessment_id}
              </div>

              <div className="bg-slate-50 rounded-lg p-4 space-y-3">
                {[
                  ['Requested By', selectedApproval.requested_by],
                  ['Status', selectedApproval.status],
                  ['Requested At', new Date(selectedApproval.requested_at).toLocaleString()],
                ].map(([label, value]) => (
                  <div key={label} className="flex justify-between items-center pb-2 border-b border-slate-200 last:border-0">
                    <span className="text-xs text-slate-500">{label}</span>
                    <span className="text-xs font-bold text-slate-800">{value}</span>
                  </div>
                ))}
              </div>

              {actionError && (
                <div className="bg-red-50 border border-red-200 rounded-lg px-3 py-2 text-xs text-red-600 font-semibold">
                  {actionError}
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-2">
                  Comments <span className="text-slate-400 font-normal">(required for rejection)</span>
                </label>
                <textarea
                  value={comments}
                  onChange={e => setComments(e.target.value)}
                  rows={3}
                  className="w-full border border-slate-200 rounded-lg px-3 py-2 text-xs outline-none focus:border-blue-500 resize-none"
                  placeholder="Add your notes or reason for decision..."
                />
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => handleAction('approve')}
                  disabled={actionLoading}
                  className="flex-1 py-2.5 bg-green-600 text-white text-xs font-bold rounded-lg hover:bg-green-700 disabled:opacity-50"
                >
                  {actionLoading ? '...' : '✓ Approve'}
                </button>
                <button
                  onClick={() => handleAction('reject')}
                  disabled={actionLoading || !comments.trim()}
                  className="flex-1 py-2.5 bg-red-600 text-white text-xs font-bold rounded-lg hover:bg-red-700 disabled:opacity-50"
                >
                  {actionLoading ? '...' : '✗ Reject'}
                </button>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}