import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { login } from '../api/jayprakashApi'

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

    try {
      const response = await login({ username, password })
      localStorage.setItem('cp4i_token', response.access_token)
      localStorage.setItem('cp4i_user', JSON.stringify(response.user))
      navigate('/')
    } catch (err) {
      setError('Invalid username or password.')
    } finally {
      setLoading(false)
    }
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

        <div className="text-center mt-6 text-xs text-slate-300">v1.0.0 — Authorized users only</div>
      </div>
    </div>
  )
}