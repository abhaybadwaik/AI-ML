import { useState, useEffect } from 'react'
import { adminAPI } from '../services/api'

interface User {
  id: number
  username: string
  email: string
  full_name: string
  role: string
  is_active: boolean
  created_at: string
}

interface SignupRequest {
  id: number
  username: string
  email: string
  full_name: string
  status: string
  requested_at: string
  reviewed_by: string | null
  reviewed_at: string | null
  reject_reason: string | null
}

const roleColors: Record<string, string> = {
  admin: 'bg-blue-100 text-blue-700',
  requester: 'bg-amber-100 text-amber-700',
}

const rolePermissions = [
  { role: 'requester', label: 'Requester', permissions: 'Submit workload requests, view own assessments and approval status' },
  { role: 'admin', label: 'Admin', permissions: 'Everything including user management, approvals, and role assignment' },
]

export default function UserManagement() {
  const [users, setUsers] = useState<User[]>([])
  const [signupRequests, setSignupRequests] = useState<SignupRequest[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'users' | 'signup'>('users')
  const [error, setError] = useState('')

  // Signup approve panel
  const [selectedRequest, setSelectedRequest] = useState<SignupRequest | null>(null)
  const [approveRole, setApproveRole] = useState('requester')
  const [rejectReason, setRejectReason] = useState('')
  const [actionMode, setActionMode] = useState<'approve' | 'reject' | null>(null)
  const [actionLoading, setActionLoading] = useState(false)
  const [actionError, setActionError] = useState('')

  // Get current logged-in user id to prevent self-delete
  const currentUser = JSON.parse(localStorage.getItem('cp4i_user') || '{}')

  useEffect(() => {
    fetchAll()
  }, [])

  const fetchAll = async () => {
    try {
      setLoading(true)
      setError('')
      const [usersRes, signupRes] = await Promise.all([
        adminAPI.getUsers(),
        adminAPI.getSignupRequests('all'),
      ])
      setUsers(Array.isArray(usersRes.data) ? usersRes.data : [])
      setSignupRequests(Array.isArray(signupRes.data) ? signupRes.data : [])
    } catch (err) {
      setError('Failed to load data.')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (user: User) => {
    if (!window.confirm(`Delete user "${user.username}"? This cannot be undone.`)) return
    try {
      await adminAPI.deleteUser(user.id)
      await fetchAll()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Delete failed.')
    }
  }

  const handleSignupAction = async () => {
    if (!selectedRequest) return
    setActionLoading(true)
    setActionError('')
    try {
      if (actionMode === 'approve') {
        await adminAPI.approveSignupRequest(selectedRequest.id, approveRole)
      } else {
        await adminAPI.rejectSignupRequest(selectedRequest.id, rejectReason || undefined)
      }
      await fetchAll()
      setSelectedRequest(null)
      setActionMode(null)
    } catch (err: any) {
      setActionError(err.response?.data?.detail || 'Action failed.')
    } finally {
      setActionLoading(false)
    }
  }

  const pendingSignups = signupRequests.filter(r => r.status === 'pending')

  const tabs = [
    { key: 'users', label: `Users (${users.length})` },
    { key: 'signup', label: `Signup Requests (${pendingSignups.length} pending)` },
  ]

  return (
    <div className="space-y-4">

      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="text-sm font-bold text-slate-800">User Management</div>
        <span className="bg-slate-100 text-slate-500 text-xs font-bold px-2 py-0.5 rounded">Admin Only</span>
        <div className="ml-auto">
          <button
            onClick={fetchAll}
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
            onClick={() => setActiveTab(tab.key as 'users' | 'signup')}
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
          <button onClick={fetchAll} className="ml-3 underline">Retry</button>
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

      {/* Users Table */}
      {!loading && activeTab === 'users' && (
        <div className="bg-white rounded-xl border border-slate-200">
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-slate-100">
                  {['Full Name', 'Username', 'Email', 'Role', 'Status', 'Created At', 'Actions'].map(h => (
                    <th key={h} className="text-left py-3 px-4 text-slate-400 font-bold uppercase tracking-wide whitespace-nowrap">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {users.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-12 text-center text-slate-400 font-semibold">No users found.</td>
                  </tr>
                ) : (
                  users.map(user => (
                    <tr key={user.id} className={`border-b border-slate-50 hover:bg-slate-50 ${!user.is_active ? 'opacity-50' : ''}`}>
                      <td className="py-3 px-4 font-semibold text-slate-800">{user.full_name}</td>
                      <td className="py-3 px-4 text-slate-500">{user.username}</td>
                      <td className="py-3 px-4 text-slate-500">{user.email}</td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${roleColors[user.role] || 'bg-slate-100 text-slate-600'}`}>
                          {user.role}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${user.is_active ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-500'}`}>
                          {user.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-400">
                        {new Date(user.created_at).toLocaleDateString()}
                      </td>
                      <td className="py-3 px-4">
                        {user.id !== currentUser.id && (
                          <button
                            onClick={() => handleDelete(user)}
                            className="px-2 py-1 border border-red-200 text-red-600 text-xs font-semibold rounded hover:bg-red-50"
                          >
                            Delete
                          </button>
                        )}
                        {user.id === currentUser.id && (
                          <span className="text-xs text-slate-400 italic">You</span>
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

      {/* Signup Requests Table */}
      {!loading && activeTab === 'signup' && (
        <div className="bg-white rounded-xl border border-slate-200">
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-slate-100">
                  {['Full Name', 'Username', 'Email', 'Status', 'Requested At', 'Reviewed By', 'Actions'].map(h => (
                    <th key={h} className="text-left py-3 px-4 text-slate-400 font-bold uppercase tracking-wide whitespace-nowrap">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {signupRequests.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-12 text-center text-slate-400 font-semibold">No signup requests.</td>
                  </tr>
                ) : (
                  signupRequests.map(req => (
                    <tr key={req.id} className="border-b border-slate-50 hover:bg-slate-50">
                      <td className="py-3 px-4 font-semibold text-slate-800">{req.full_name}</td>
                      <td className="py-3 px-4 text-slate-500">{req.username}</td>
                      <td className="py-3 px-4 text-slate-500">{req.email}</td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${
                          req.status === 'pending' ? 'bg-amber-100 text-amber-700'
                          : req.status === 'approved' ? 'bg-green-100 text-green-700'
                          : 'bg-red-100 text-red-700'
                        }`}>
                          {req.status.charAt(0).toUpperCase() + req.status.slice(1)}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-400">
                        {new Date(req.requested_at).toLocaleDateString()}
                      </td>
                      <td className="py-3 px-4 text-slate-500">{req.reviewed_by ?? '—'}</td>
                      <td className="py-3 px-4">
                        {req.status === 'pending' ? (
                          <button
                            onClick={() => { setSelectedRequest(req); setActionMode('approve'); setApproveRole('requester'); setRejectReason(''); setActionError('') }}
                            className="px-3 py-1.5 bg-blue-600 text-white text-xs font-bold rounded-lg hover:bg-blue-700"
                          >
                            Review
                          </button>
                        ) : (
                          <span className={`text-xs font-bold ${req.status === 'approved' ? 'text-green-600' : 'text-red-600'}`}>
                            {req.status === 'approved' ? '✓ Approved' : '✗ Rejected'}
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

      {/* Role Reference */}
      <div className="bg-white rounded-xl border border-slate-200 p-5">
        <div className="text-sm font-bold text-slate-800 mb-4">Role Reference</div>
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-slate-100">
              <th className="text-left py-2 px-3 text-slate-400 font-bold uppercase tracking-wide">Role</th>
              <th className="text-left py-2 px-3 text-slate-400 font-bold uppercase tracking-wide">What They Can Do</th>
            </tr>
          </thead>
          <tbody>
            {rolePermissions.map(r => (
              <tr key={r.role} className="border-b border-slate-50">
                <td className="py-2 px-3">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${roleColors[r.role]}`}>
                    {r.label}
                  </span>
                </td>
                <td className="py-2 px-3 text-slate-600">{r.permissions}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Review Signup Panel */}
      {selectedRequest && (
        <>
          <div className="fixed inset-0 bg-black/20 z-40" onClick={() => setSelectedRequest(null)} />
          <div className="fixed right-0 top-0 bottom-0 w-96 bg-white border-l border-slate-200 z-50 overflow-y-auto shadow-2xl">
            <div className="p-6 space-y-4">
              <div className="flex items-center justify-between">
                <div className="text-sm font-bold text-slate-800">Review Signup Request</div>
                <button onClick={() => setSelectedRequest(null)} className="text-slate-400 hover:text-slate-600 font-bold text-lg">✕</button>
              </div>

              <div className="bg-slate-50 rounded-lg p-4 space-y-3">
                {[
                  ['Full Name', selectedRequest.full_name],
                  ['Username', selectedRequest.username],
                  ['Email', selectedRequest.email],
                  ['Requested At', new Date(selectedRequest.requested_at).toLocaleString()],
                ].map(([label, value]) => (
                  <div key={label} className="flex justify-between items-center pb-2 border-b border-slate-200 last:border-0">
                    <span className="text-xs text-slate-500">{label}</span>
                    <span className="text-xs font-bold text-slate-800">{value}</span>
                  </div>
                ))}
              </div>

              {/* Mode Toggle */}
              <div className="flex gap-2">
                <button
                  onClick={() => setActionMode('approve')}
                  className={`flex-1 py-2 text-xs font-bold rounded-lg border transition-colors ${actionMode === 'approve' ? 'bg-green-600 text-white border-green-600' : 'border-slate-200 text-slate-600 hover:bg-slate-50'}`}
                >
                  ✓ Approve
                </button>
                <button
                  onClick={() => setActionMode('reject')}
                  className={`flex-1 py-2 text-xs font-bold rounded-lg border transition-colors ${actionMode === 'reject' ? 'bg-red-600 text-white border-red-600' : 'border-slate-200 text-slate-600 hover:bg-slate-50'}`}
                >
                  ✗ Reject
                </button>
              </div>

              {/* Approve: pick role */}
              {actionMode === 'approve' && (
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Assign Role</label>
                  <select
                    value={approveRole}
                    onChange={e => setApproveRole(e.target.value)}
                    className="w-full border border-slate-200 rounded-lg px-3 py-2 text-xs outline-none focus:border-blue-500"
                  >
                    <option value="requester">Requester</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>
              )}

              {/* Reject: reason */}
              {actionMode === 'reject' && (
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Reason <span className="text-slate-400 font-normal">(optional)</span>
                  </label>
                  <textarea
                    value={rejectReason}
                    onChange={e => setRejectReason(e.target.value)}
                    rows={3}
                    className="w-full border border-slate-200 rounded-lg px-3 py-2 text-xs outline-none focus:border-blue-500 resize-none"
                    placeholder="Reason for rejection..."
                  />
                </div>
              )}

              {actionError && (
                <div className="bg-red-50 border border-red-200 rounded-lg px-3 py-2 text-xs text-red-600 font-semibold">
                  {actionError}
                </div>
              )}

              <button
                onClick={handleSignupAction}
                disabled={actionLoading || !actionMode}
                className="w-full py-2.5 bg-blue-600 text-white text-xs font-bold rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {actionLoading ? 'Processing...' : actionMode === 'approve' ? 'Confirm Approve' : actionMode === 'reject' ? 'Confirm Reject' : 'Select an action'}
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}