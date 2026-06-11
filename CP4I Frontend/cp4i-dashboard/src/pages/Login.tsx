import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function Login() {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleLogin = async () => {
    if (!username || !password) {
      setError('Please enter both username and password.')
      return
    }

    setLoading(true)
    setError('')

    // Mock login — replace with real API later
    setTimeout(() => {
      const mockUsers: Record<string, { name: string; role: string }> = {
        'abhay.admin': { name: 'Abhay', role: 'admin' },
        'sumith.ops': { name: 'Sumith', role: 'operations' },
        'pratik.eng': { name: 'Pratik', role: 'requestor' },
        'prakash.appr': { name: 'Jayprakash', role: 'approver' },
        'mgr.bank': { name: 'Bank Manager', role: 'management' },
      }

      const user = mockUsers[username]

      if (user && password === 'password123') {
        // Store in localStorage
        localStorage.setItem('cp4i_token', 'mock-jwt-token-12345')
        localStorage.setItem('cp4i_user', JSON.stringify({
          username,
          name: user.name,
          role: user.role,
        }))
        navigate('/')
      } else {
        setError('Invalid username or password.')
      }
      setLoading(false)
    }, 800)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleLogin()
  }

  return (
    <div className="min-h-screen bg-slate-100 flex items-center justify-center">
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xl p-10 w-96">

        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-14 h-14 bg-slate-900 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <span className="text-white text-2xl">⚙</span>
          </div>
          <div className="text-lg font-extrabold text-slate-800">CP4I License Management</div>
          <div className="text-xs text-slate-400 mt-1">Standard Bank Mozambique — Eidiko Systems</div>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-xs text-red-600 font-semibold mb-4">
            {error}
          </div>
        )}

        {/* Username */}
        <div className="mb-4">
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            Username <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={username}
            onChange={e => setUsername(e.target.value)}
            onKeyDown={handleKeyDown}
            className="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            placeholder="Enter your username"
          />
        </div>

        {/* Password */}
        <div className="mb-6">
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            Password <span className="text-red-500">*</span>
          </label>
          <input
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            onKeyDown={handleKeyDown}
            className="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            placeholder="Enter your password"
          />
        </div>

        {/* Login Button */}
        <button
          onClick={handleLogin}
          disabled={loading}
          className="w-full py-3 bg-slate-900 text-white text-sm font-bold rounded-lg hover:bg-slate-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Logging in...' : 'Login'}
        </button>

        {/* Hint */}
        <div className="mt-6 bg-slate-50 rounded-lg p-3">
          <div className="text-xs font-bold text-slate-500 mb-2">Demo Credentials:</div>
          <div className="space-y-1 text-xs text-slate-400">
            <div><span className="font-semibold text-slate-600">abhay.admin</span> — Admin</div>
            <div><span className="font-semibold text-slate-600">sumith.ops</span> — Operations</div>
            <div><span className="font-semibold text-slate-600">prakash.appr</span> — Approver</div>
            <div className="mt-1">Password for all: <span className="font-semibold text-slate-600">password123</span></div>
          </div>
        </div>

        <div className="text-center mt-6 text-xs text-slate-300">v1.0.0 — Authorized users only</div>
      </div>
    </div>
  )
}