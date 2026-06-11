import { BrowserRouter, Routes, Route } from 'react-router-dom'
import MainLayout from './components/layout/MainLayout'
import ProtectedRoute from './components/layout/layout/ProtectedRoute'
import Dashboard from './pages/Dashboard'
import WorkloadRequest from './pages/WorkloadRequest'
import AssessmentDetail from './pages/AssessmentDetail'
import Assessments from './pages/Assessments'
import Approvals from './pages/Approvals'
import LicenseMonitoring from './pages/LicenseMonitoring'
import Reports from './pages/Reports'
import UserManagement from './pages/UserManagement'
import Login from './pages/Login'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Dashboard />} />
          <Route path="monitoring" element={<LicenseMonitoring />} />
          <Route path="request" element={<WorkloadRequest />} />
          <Route path="assessments" element={<Assessments />} />
          <Route path="assessment/:id" element={<AssessmentDetail />} />
          <Route path="approvals" element={<Approvals />} />
          <Route path="reports" element={<Reports />} />
          <Route path="users" element={<UserManagement />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App