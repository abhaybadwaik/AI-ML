import { Navigate } from 'react-router-dom'

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('cp4i_token')

  if (!token) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}