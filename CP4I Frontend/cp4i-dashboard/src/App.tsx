import { BrowserRouter, Routes, Route } from 'react-router-dom'
import MainLayout from './components/layout/MainLayout'
import Dashboard from './pages/Dashboard'
import WorkloadRequest from './pages/WorkloadRequest'
import AssessmentDetail from './pages/AssessmentDetail'
import Approvals from './pages/Approvals'
import LicenseMonitoring from './pages/LicenseMonitoring'
import Reports from './pages/Reports'
import UserManagement from './pages/UserManagement'

function Placeholder({ name }: { name: string }) {
  return (
    <div className="flex items-center justify-center h-64 bg-white rounded-xl border border-slate-200">
      <p className="text-slate-400 font-semibold">{name} — coming soon</p>
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="monitoring" element={<LicenseMonitoring />} />
          <Route path="request" element={<WorkloadRequest />} />
          <Route path="assessments" element={<Placeholder name="Assessments" />} />
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