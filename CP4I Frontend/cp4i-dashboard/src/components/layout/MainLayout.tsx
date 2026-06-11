import { Outlet, useLocation } from 'react-router-dom'
import Sidebar from './Sidebar'

const pageTitles: Record<string, { title: string; breadcrumb: string }> = {
  '/': { title: 'Dashboard', breadcrumb: 'Home / Dashboard' },
  '/monitoring': { title: 'License Monitoring', breadcrumb: 'Home / License Monitoring' },
  '/request': { title: 'New Workload Request', breadcrumb: 'Home / Workload Requests / New' },
  '/assessments': { title: 'Assessments', breadcrumb: 'Home / Assessments' },
  '/approvals': { title: 'Approval Queue', breadcrumb: 'Home / Approvals' },
  '/reports': { title: 'Reports', breadcrumb: 'Home / Reports' },
  '/users': { title: 'User Management', breadcrumb: 'Home / Admin / Users' },
}

export default function MainLayout() {
  const location = useLocation()
  const page = pageTitles[location.pathname] || { title: 'CP4I', breadcrumb: 'Home' }

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Topbar */}
        <div className="h-14 bg-white border-b border-slate-200 flex items-center px-6 gap-4 flex-shrink-0">
          <div>
            <div className="text-sm font-bold text-slate-800">{page.title}</div>
            <div className="text-xs text-slate-400">{page.breadcrumb}</div>
          </div>
          <div className="ml-auto flex items-center gap-2">
            <button className="px-3 py-1.5 text-xs font-semibold border border-blue-600 text-blue-600 rounded-md hover:bg-blue-50 transition-colors">
              + New Workload Request
            </button>
            <button className="px-3 py-1.5 text-xs font-semibold bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
              ↺ Refresh License Data
            </button>
          </div>
        </div>

        {/* Page Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </div>
      </div>
    </div>
  )
}