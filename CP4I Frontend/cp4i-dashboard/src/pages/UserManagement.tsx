import { useState, useEffect } from 'react'
import api from '../services/api'

interface User {
  id: number
  fullName: string
  username: string
  email: string
  role: string
  status: string
  lastLogin: string
}

const roleColors: Record<string, string> = {
  Admin: 'bg-blue-100 text-blue-700',
  Operations: 'bg-green-100 text-green-700',
  Requestor: 'bg-amber-100 text-amber-700',
  Approver: 'bg-red-100 text-red-700',
  Management: 'bg-slate-100 text-slate-600',
}

const rolePermissions = [
  { role: 'Requestor', permissions: 'Submit workload requests, view own assessments and approval status' },
  { role: 'Approver', permissions: 'Review and approve or reject assessments, view all requests' },
  { role: 'Operations', permissions: 'Trigger ingestion, upload PDFs, view all monitoring data, submit requests' },
  { role: 'Management', permissions: 'View all screens read-only, download all reports' },
  { role: 'Admin', permissions: 'Everything including user creation, deactivation, and role assignment' },
]

export default function UserManagement() {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [showPanel, setShowPanel] = useState(false)
  const [editUser, setEditUser] = useState<User | null>(null)
  const [form, setForm] = useState({ fullName: '', username: '', email: '', role: 'Requestor' })
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async () => {
    try {
      setLoading(true)
      const response = await api.get('/users')
      setUsers(response.data)
    } catch (err) {
      console.error('Failed to load users:', err)
    } finally {
      setLoading(false)
    }
  }

  const openAdd = () => {
    setEditUser(null)
    setForm({ fullName: '', username: '', email: '', role: 'Requestor' })
    setShowPanel(true)
  }

  const openEdit = (user: User) => {
    setEditUser(user)
    setForm({ fullName: user.fullName, username: user.username, email: user.email, role: user.role })
    setShowPanel(true)
  }

  const handleSave = async () => {
    if (!form.fullName || !form.username || !form.email) {
      alert('Please fill all fields.')
      return
    }
    setSaving(true)
    try {
      if (editUser) {
        await api.patch(`/users/${editUser.id}`, form)
        alert(`User updated!\nPATCH /users/${editUser.id}`)
      } else {
        await api.post('/users', { ...form, status: 'Active', lastLogin: 'Never' })
        alert('User created!\nPOST /users\nTemporary password sent to email.')
      }
      await fetchUsers()
      setShowPanel(false)
    } catch (err) {
      alert('Save failed. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  const handleDeactivate = async (user: User) => {
    try {
      await api.patch(`/users/${user.id}`, {
        status: user.status === 'Active' ? 'Inactive' : 'Active'
      })
      await fetchUsers()
    } catch (err) {
      alert('Action failed.')
    }
  }

  return (
    <div className="space-y-4">

      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="text-sm font-bold text-slate-800">User Management</div>
        <span className="bg-slate-100 text-slate-500 text-xs font-bold px-2 py-0.5 rounded">Admin Only</span>
        <div className="ml-auto flex gap-2">
          <button
            onClick={fetchUsers}
            className="px-3 py-1.5 text-xs font-semibold border border-slate-200 text-slate-600 rounded-lg hover:bg-slate-50"
          >
            ↺ Refresh
          </button>
          <button
            onClick={openAdd}
            className="px-4 py-2 bg-blue-600 text-white text-xs font-bold rounded-lg hover:bg-blue-700"
          >
            + Add New User
          </button>
        </div>
      </div>

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
      {!loading && (
        <div className="bg-white rounded-xl border border-slate-200">
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-slate-100">
                  {['Full Name', 'Username', 'Email', 'Role', 'Status', 'Last Login', 'Actions'].map(h => (
                    <th key={h} className="text-left py-3 px-4 text-slate-400 font-bold uppercase tracking-wide whitespace-nowrap">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {users.map(user => (
                  <tr key={user.id} className={`border-b border-slate-50 hover:bg-slate-50 ${user.status === 'Inactive' ? 'opacity-50' : ''}`}>
                    <td className="py-3 px-4 font-semibold text-slate-800">{user.fullName}</td>
                    <td className="py-3 px-4 text-slate-500">{user.username}</td>
                    <td className="py-3 px-4 text-slate-500">{user.email}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${roleColors[user.role] || 'bg-slate-100 text-slate-600'}`}>
                        {user.role}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${user.status === 'Active' ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-500'}`}>
                        {user.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-400">{user.lastLogin}</td>
                    <td className="py-3 px-4">
                      <div className="flex gap-2">
                        <button
                          onClick={() => openEdit(user)}
                          className="px-2 py-1 border border-slate-200 text-slate-600 text-xs font-semibold rounded hover:bg-slate-50"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDeactivate(user)}
                          className={`px-2 py-1 border text-xs font-semibold rounded transition-colors
                            ${user.status === 'Active'
                              ? 'border-red-200 text-red-600 hover:bg-red-50'
                              : 'border-green-200 text-green-600 hover:bg-green-50'
                            }`}
                        >
                          {user.status === 'Active' ? 'Deactivate' : 'Activate'}
                        </button>
                        <button
                          onClick={() => alert(`Password reset email sent to ${user.email}`)}
                          className="px-2 py-1 border border-slate-200 text-slate-600 text-xs font-semibold rounded hover:bg-slate-50"
                        >
                          Reset Pwd
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
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
                    {r.role}
                  </span>
                </td>
                <td className="py-2 px-3 text-slate-600">{r.permissions}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Add/Edit Panel */}
      {showPanel && (
        <>
          <div className="fixed inset-0 bg-black/20 z-40" onClick={() => setShowPanel(false)} />
          <div className="fixed right-0 top-0 bottom-0 w-96 bg-white border-l border-slate-200 z-50 overflow-y-auto shadow-2xl">
            <div className="p-6 space-y-4">
              <div className="flex items-center justify-between">
                <div className="text-sm font-bold text-slate-800">
                  {editUser ? 'Edit User' : 'Add New User'}
                </div>
                <button onClick={() => setShowPanel(false)} className="text-slate-400 hover:text-slate-600 font-bold text-lg">✕</button>
              </div>

              {[
                { label: 'Full Name', key: 'fullName', placeholder: 'e.g. John Smith' },
                { label: 'Username', key: 'username', placeholder: 'e.g. john.smith' },
                { label: 'Email', key: 'email', placeholder: 'e.g. john@eidiko.com' },
              ].map(field => (
                <div key={field.key}>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    {field.label} <span className="text-red-500">*</span>
                  </label>
                  <input
                    value={form[field.key as keyof typeof form]}
                    onChange={e => setForm(p => ({ ...p, [field.key]: e.target.value }))}
                    className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                    placeholder={field.placeholder}
                  />
                </div>
              ))}

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Role <span className="text-red-500">*</span>
                </label>
                <select
                  value={form.role}
                  onChange={e => setForm(p => ({ ...p, role: e.target.value }))}
                  className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-500"
                >
                  {Object.keys(roleColors).map(r => (
                    <option key={r} value={r}>{r}</option>
                  ))}
                </select>
              </div>

              {!editUser && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-xs text-blue-700">
                  A temporary password will be auto-generated and sent to the user's email on save.
                </div>
              )}

              <div className="flex gap-2 pt-2">
                <button
                  onClick={handleSave}
                  disabled={saving}
                  className="flex-1 py-2.5 bg-blue-600 text-white text-xs font-bold rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {saving ? 'Saving...' : editUser ? 'Save Changes' : 'Create User'}
                </button>
                <button
                  onClick={() => setShowPanel(false)}
                  className="flex-1 py-2.5 border border-slate-200 text-slate-600 text-xs font-bold rounded-lg hover:bg-slate-50"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}