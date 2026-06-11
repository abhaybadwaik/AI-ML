import { useState } from 'react'

const initialUsers = [
  { id: 1, fullName: 'Abhay Badwaik', username: 'abhay.admin', email: 'abhay@eidiko.com', role: 'Admin', status: 'Active', lastLogin: '10-Jun-2026 09:15' },
  { id: 2, fullName: 'Sumith Kumar', username: 'sumith.ops', email: 'sumith@eidiko.com', role: 'Operations', status: 'Active', lastLogin: '10-Jun-2026 08:50' },
  { id: 3, fullName: 'Pratik Sharma', username: 'pratik.eng', email: 'pratik@eidiko.com', role: 'Requestor', status: 'Active', lastLogin: '09-Jun-2026 17:30' },
  { id: 4, fullName: 'Jayprakash', username: 'prakash.appr', email: 'prakash@eidiko.com', role: 'Approver', status: 'Active', lastLogin: '10-Jun-2026 10:02' },
  { id: 5, fullName: 'Bank Manager', username: 'mgr.bank', email: 'manager@standardbank.co.mz', role: 'Management', status: 'Active', lastLogin: '08-Jun-2026 14:20' },
  { id: 6, fullName: 'John Doe', username: 'john.req', email: 'john@standardbank.co.mz', role: 'Requestor', status: 'Inactive', lastLogin: '01-May-2026 09:00' },
]

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

type User = typeof initialUsers[0]

export default function UserManagement() {
  const [users, setUsers] = useState(initialUsers)
  const [showPanel, setShowPanel] = useState(false)
  const [editUser, setEditUser] = useState<User | null>(null)
  const [form, setForm] = useState({ fullName: '', username: '', email: '', role: 'Requestor' })

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

  const handleSave = () => {
    if (!form.fullName || !form.username || !form.email) {
      alert('Please fill all fields.')
      return
    }
    if (editUser) {
      setUsers(prev => prev.map(u => u.id === editUser.id ? { ...u, ...form } : u))
      alert(`User updated!\nPATCH /users/${editUser.id}`)
    } else {
      const newUser: User = {
        id: users.length + 1,
        ...form,
        status: 'Active',
        lastLogin: 'Never',
      }
      setUsers(prev => [...prev, newUser])
      alert('User created!\nPOST /users\nTemporary password sent to email.')
    }
    setShowPanel(false)
  }

  const handleDeactivate = (user: User) => {
    setUsers(prev => prev.map(u =>
      u.id === user.id
        ? { ...u, status: u.status === 'Active' ? 'Inactive' : 'Active' }
        : u
    ))
  }

  return (
    <div className="space-y-4">

      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="text-sm font-bold text-slate-800">User Management</div>
        <span className="bg-slate-100 text-slate-500 text-xs font-bold px-2 py-0.5 rounded">Admin Only</span>
        <div className="ml-auto">
          <button
            onClick={openAdd}
            className="px-4 py-2 bg-blue-600 text-white text-xs font-bold rounded-lg hover:bg-blue-700 transition-colors"
          >
            + Add New User
          </button>
        </div>
      </div>

      {/* Users Table */}
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
                    <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${roleColors[user.role]}`}>
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

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Full Name <span className="text-red-500">*</span></label>
                <input
                  value={form.fullName}
                  onChange={e => setForm(p => ({ ...p, fullName: e.target.value }))}
                  className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                  placeholder="e.g. John Smith"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Username <span className="text-red-500">*</span></label>
                <input
                  value={form.username}
                  onChange={e => setForm(p => ({ ...p, username: e.target.value }))}
                  className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                  placeholder="e.g. john.smith"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Email <span className="text-red-500">*</span></label>
                <input
                  type="email"
                  value={form.email}
                  onChange={e => setForm(p => ({ ...p, email: e.target.value }))}
                  className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                  placeholder="e.g. john@eidiko.com"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Role <span className="text-red-500">*</span></label>
                <select
                  value={form.role}
                  onChange={e => setForm(p => ({ ...p, role: e.target.value }))}
                  className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
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
                  className="flex-1 py-2.5 bg-blue-600 text-white text-xs font-bold rounded-lg hover:bg-blue-700 transition-colors"
                >
                  {editUser ? 'Save Changes' : 'Create User'}
                </button>
                <button
                  onClick={() => setShowPanel(false)}
                  className="flex-1 py-2.5 border border-slate-200 text-slate-600 text-xs font-bold rounded-lg hover:bg-slate-50 transition-colors"
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