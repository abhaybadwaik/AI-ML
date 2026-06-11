import { NavLink } from 'react-router-dom'

const navItems = [
  { label: 'Dashboard', path: '/', icon: '▦' },
  { label: 'License Monitoring', path: '/monitoring', icon: '◉' },
  { label: 'New Request', path: '/request', icon: '+' },
  { label: 'Assessments', path: '/assessments', icon: '≡' },
  { label: 'Approvals', path: '/approvals', icon: '✓', badge: 3 },
  { label: 'Reports', path: '/reports', icon: '↓' },
  { label: 'User Management', path: '/users', icon: '⚇' },
]

export default function Sidebar() {
  return (
    <div className="w-56 bg-slate-900 flex flex-col h-screen flex-shrink-0">
      {/* Logo */}
      <div className="px-4 py-5 border-b border-slate-700">
        <div className="text-white font-bold text-sm leading-snug">
          CP4I License Management
        </div>
        <div className="text-slate-400 text-xs mt-1">Standard Bank Mozambique</div>
      </div>

      {/* User */}
      <div className="px-4 py-3 border-b border-slate-700 flex items-center gap-3">
        <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
          AB
        </div>
        <div>
          <div className="text-white text-xs font-semibold">Abhay</div>
          <div className="text-slate-400 text-xs">Admin</div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-3">
        <div className="px-4 py-2 text-slate-500 text-xs font-bold uppercase tracking-widest">
          Main
        </div>
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-2 text-xs cursor-pointer border-l-2 transition-all
              ${isActive
                ? 'bg-blue-900/40 text-white border-blue-500'
                : 'text-slate-400 border-transparent hover:bg-slate-800 hover:text-white'
              }`
            }
          >
            <span className="w-4 text-center">{item.icon}</span>
            <span className="flex-1">{item.label}</span>
            {item.badge && (
              <span className="bg-red-500 text-white text-xs font-bold px-2 py-0.5 rounded-full">
                {item.badge}
              </span>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Logout */}
      <div className="px-4 py-4 border-t border-slate-700">
        <button className="text-slate-400 text-xs hover:text-white transition-colors">
          ⎋ Logout
        </button>
      </div>
    </div>
  )
}