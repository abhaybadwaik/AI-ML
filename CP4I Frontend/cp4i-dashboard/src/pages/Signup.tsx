import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { authAPI } from '../services/api'

export default function Signup() {
  const navigate = useNavigate()

  const [form, setForm] = useState({
    full_name: '',
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }))
    setError('')
  }

  const validate = () => {
    if (!form.full_name.trim()) return 'Full name is required.'
    if (!form.username.trim()) return 'Username is required.'
    if (!form.email.trim()) return 'Email is required.'
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) return 'Enter a valid email address.'
    if (!form.password) return 'Password is required.'
    if (form.password.length < 6) return 'Password must be at least 6 characters.'
    if (form.password !== form.confirmPassword) return 'Passwords do not match.'
    return ''
  }

  const handleSignup = async () => {
    const validationError = validate()
    if (validationError) { setError(validationError); return }

    setLoading(true)
    setError('')

    try {
      await authAPI.signup(form.username, form.email, form.full_name, form.password)
      setSuccess(true)
    } catch (err: any) {
      const detail = err.response?.data?.detail
      if (err.response?.status === 409) {
        setError(detail || 'Email already registered or request already pending.')
      } else {
        setError('Something went wrong. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleSignup()
  }

  // ── Success State ─────────────────────────────────────────
  if (success) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center">
        <div className="bg-white rounded-2xl border border-slate-200 shadow-xl p-10 w-96 text-center">
          <div className="w-14 h-14 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-green-600 text-2xl">✓</span>
          </div>
          <h2 className="text-lg font-extrabold text-slate-800 mb-2">Request Submitted!</h2>
          <p className="text-sm text-slate-500 mb-6">
            Your signup request has been sent to the administrator. You will receive an email once your account is approved.
          </p>
          <button
            onClick={() => navigate('/login')}
            className="w-full py-3 bg-slate-900 text-white text-sm font-bold rounded-lg hover:bg-slate-800 transition-colors"
          >
            Back to Login
          </button>
        </div>
      </div>
    )
  }

  // ── Signup Form ───────────────────────────────────────────
  return (
    <div className="min-h-screen bg-slate-100 flex items-center justify-center">
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xl p-10 w-96">

        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-14 h-14 bg-slate-900 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <span className="text-white text-2xl">⚙</span>
          </div>
          <div className="text-lg font-extrabold text-slate-800">Create Account</div>
          <div className="text-xs text-slate-400 mt-1">CP4I License Management — Eidiko Systems</div>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-xs text-red-600 font-semibold mb-4">
            {error}
          </div>
        )}

        {/* Full Name */}
        <div className="mb-4">
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            Full Name <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            name="full_name"
            value={form.full_name}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            className="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            placeholder="John Doe"
          />
        </div>

        {/* Username */}
        <div className="mb-4">
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            Username <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            name="username"
            value={form.username}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            className="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            placeholder="john_doe"
          />
        </div>

        {/* Email */}
        <div className="mb-4">
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            Email <span className="text-red-500">*</span>
          </label>
          <input
            type="email"
            name="email"
            value={form.email}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            className="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            placeholder="john@example.com"
          />
        </div>

        {/* Password */}
        <div className="mb-4">
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            Password <span className="text-red-500">*</span>
          </label>
          <input
            type="password"
            name="password"
            value={form.password}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            className="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            placeholder="Min. 6 characters"
          />
        </div>

        {/* Confirm Password */}
        <div className="mb-6">
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            Confirm Password <span className="text-red-500">*</span>
          </label>
          <input
            type="password"
            name="confirmPassword"
            value={form.confirmPassword}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            className="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            placeholder="Re-enter your password"
          />
        </div>

        {/* Submit */}
        <button
          onClick={handleSignup}
          disabled={loading}
          className="w-full py-3 bg-slate-900 text-white text-sm font-bold rounded-lg hover:bg-slate-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Submitting...' : 'Request Access'}
        </button>

        {/* Back to Login */}
        <p className="text-center text-xs text-slate-400 mt-5">
          Already have an account?{' '}
          <button
            onClick={() => navigate('/login')}
            className="text-blue-600 font-semibold hover:underline"
          >
            Login
          </button>
        </p>
      </div>
    </div>
  )
}