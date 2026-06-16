import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { authAPI } from '../services/api'

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
      const response = await authAPI.login(username, password)
      localStorage.setItem('cp4i_token', response.data.access_token)
      localStorage.setItem('cp4i_user', JSON.stringify({
        id: response.data.user_id,
        username: response.data.username,
        full_name: response.data.full_name,
        role: response.data.role,
      }))
      navigate('/')
    } catch (err: any) {
      if (err.response?.status === 403) {
        setError('Your account is inactive. Please contact the administrator.')
      } else {
        setError('Invalid username or password.')
      }
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
            placeholder="Enter your username or email"
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

        {/* Signup Link */}
        <p className="text-center text-xs text-slate-400 mt-5">
          Don't have an account?{' '}
          <button
            onClick={() => navigate('/signup')}
            className="text-blue-600 font-semibold hover:underline"
          >
            Request Access
          </button>
        </p>

        <div className="text-center mt-4 text-xs text-slate-300">v1.0.0 — Authorized users only</div>
      </div>
    </div>
  )
}