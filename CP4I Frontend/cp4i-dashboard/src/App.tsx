import { BrowserRouter, Routes, Route } from 'react-router-dom'
import MainLayout from './components/layout/MainLayout'
import Dashboard from './pages/Dashboard'

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
          <Route path="monitoring" element={<Placeholder name="License Monitoring" />} />
          <Route path="request" element={<Placeholder name="Workload Request" />} />
          <Route path="assessments" element={<Placeholder name="Assessments" />} />
          <Route path="approvals" element={<Placeholder name="Approvals" />} />
          <Route path="reports" element={<Placeholder name="Reports" />} />
          <Route path="users" element={<Placeholder name="User Management" />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App