import { clusterData, recentAssessments, pendingApprovals } from '../data/mockData'

const recommendationColor: Record<string, string> = {
  Proceed: 'bg-green-100 text-green-700',
  Hold: 'bg-amber-100 text-amber-700',
  Reject: 'bg-red-100 text-red-700',
}

const riskColor: Record<string, string> = {
  Low: 'bg-green-100 text-green-700',
  Medium: 'bg-amber-100 text-amber-700',
  High: 'bg-red-100 text-red-700',
  Critical: 'bg-red-200 text-red-800',
}

const statusColor: Record<string, string> = {
  Pending: 'bg-amber-100 text-amber-700',
  Approved: 'bg-blue-100 text-blue-700',
  Rejected: 'bg-red-100 text-red-700',
}

function Badge({ label, colorClass }: { label: string; colorClass: string }) {
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${colorClass}`}>
      {label}
    </span>
  )
}

function KpiCard({ label, value, sub, valueColor }: {
  label: string; value: string | number; sub: string; valueColor?: string
}) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5">
      <div className="text-xs font-bold text-slate-400 uppercase tracking-wide">{label}</div>
      <div className={`text-3xl font-extrabold mt-2 ${valueColor || 'text-slate-800'}`}>{value}</div>
      <div className="text-xs text-slate-400 mt-1">{sub}</div>
    </div>
  )
}

function ClusterCard({ cluster }: { cluster: typeof clusterData[0] }) {
  const pct = Math.round((cluster.totalVpcs / cluster.limitVpcs) * 100)
  const barColor = pct >= 80 ? 'bg-red-500' : pct >= 60 ? 'bg-amber-400' : 'bg-blue-500'

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5">
      <div className="text-xs font-bold text-slate-400 uppercase tracking-wide">
        {cluster.name}
      </div>
      <div className="text-2xl font-extrabold text-slate-800 mt-1">
        {cluster.totalVpcs} <span className="text-sm font-medium text-slate-400">VPCs</span>
      </div>
      <div className="w-full bg-slate-100 rounded-full h-2 mt-3">
        <div
          className={`h-2 rounded-full ${barColor}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <div className="text-xs text-slate-400 mt-1">{pct}% of {cluster.limitVpcs} VPC limit</div>
      <div className="flex flex-wrap gap-1 mt-3">
        {cluster.products.map(p => (
          <span key={p.name} className="bg-blue-50 text-blue-700 text-xs font-bold px-2 py-0.5 rounded">
            {p.name} {p.vpcs}
          </span>
        ))}
      </div>
      <div className="text-xs text-slate-400 mt-2">Last updated: {cluster.lastUpdated}</div>
    </div>
  )
}

export default function Dashboard() {
  const totalVpcs = clusterData.reduce((sum, c) => sum + c.totalVpcs, 0)
  const totalLimit = clusterData.reduce((sum, c) => sum + c.limitVpcs, 0)

  return (
    <div className="space-y-6">

      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-4">
        <KpiCard label="Total VPCs Used" value={totalVpcs} sub="Across all 3 clusters" valueColor="text-blue-600" />
        <KpiCard label="Available Headroom" value={totalLimit - totalVpcs} sub={`Before licensed limit (${totalLimit} VPC)`} valueColor="text-green-600" />
        <KpiCard label="Pending Approvals" value={pendingApprovals.length} sub="Awaiting admin decision" valueColor="text-amber-600" />
        <KpiCard label="Active Requests" value={7} sub="In progress this month" />
      </div>

      {/* Cluster Cards */}
      <div className="grid grid-cols-3 gap-4">
        {clusterData.map(c => <ClusterCard key={c.key} cluster={c} />)}
      </div>

      {/* Bottom Section */}
      <div className="grid grid-cols-2 gap-4">

        {/* Recent Assessments */}
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="text-sm font-bold text-slate-800">Recent Assessments</div>
            <button className="text-xs text-blue-600 font-semibold hover:underline">View All</button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-slate-100">
                  <th className="text-left py-2 px-2 text-slate-400 font-bold uppercase tracking-wide">Workload</th>
                  <th className="text-left py-2 px-2 text-slate-400 font-bold uppercase tracking-wide">Product</th>
                  <th className="text-left py-2 px-2 text-slate-400 font-bold uppercase tracking-wide">VPCs</th>
                  <th className="text-left py-2 px-2 text-slate-400 font-bold uppercase tracking-wide">Rec.</th>
                  <th className="text-left py-2 px-2 text-slate-400 font-bold uppercase tracking-wide">Status</th>
                </tr>
              </thead>
              <tbody>
                {recentAssessments.map(a => (
                  <tr key={a.id} className="border-b border-slate-50 hover:bg-slate-50">
                    <td className="py-2 px-2 font-medium text-slate-700">{a.workload}</td>
                    <td className="py-2 px-2 text-slate-500">{a.product}</td>
                    <td className="py-2 px-2 text-slate-700 font-semibold">{a.requiredVpc}</td>
                    <td className="py-2 px-2"><Badge label={a.recommendation} colorClass={recommendationColor[a.recommendation]} /></td>
                    <td className="py-2 px-2"><Badge label={a.status} colorClass={statusColor[a.status]} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Pending Approvals */}
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="text-sm font-bold text-slate-800">Pending Approvals</div>
            <button className="text-xs text-blue-600 font-semibold hover:underline">View All</button>
          </div>
          <div className="space-y-3">
            {pendingApprovals.map(a => (
              <div key={a.id} className="flex items-center gap-3 p-3 rounded-lg border border-slate-100 hover:bg-slate-50">
                <div className="flex-1">
                  <div className="text-xs font-semibold text-slate-800">{a.workload}</div>
                  <div className="flex gap-2 mt-1">
                    <Badge label={a.risk} colorClass={riskColor[a.risk]} />
                    <Badge label={a.recommendation} colorClass={recommendationColor[a.recommendation]} />
                  </div>
                </div>
                <button className="px-3 py-1.5 text-xs font-semibold border border-blue-600 text-blue-600 rounded-md hover:bg-blue-50 transition-colors">
                  Review
                </button>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  )
}