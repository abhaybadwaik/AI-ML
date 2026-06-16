import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { licenseAPI, assessmentAPI, approvalAPI } from '../services/api'

interface LicenseSnapshot {
  id: number
  cluster: string
  product_name: string
  measured_quantity: number
  converted_quantity: number
  source_type: string
  report_date: string
  collected_at: string
}

interface ClusterSnapshot {
  cluster: string
  total_vpcs: number
  limit_vpcs: number
  last_updated: string
  products: { product_name: string; converted_quantity: number }[]
}

interface Assessment {
  id: string
  workload_name: string
  product_type: string
  required_vpc: number
  recommendation: string
  risk_level: string
  status: string
  assessed_at: string
}

interface Approval {
  id: number
  assessment_id: number
  status: string
  requested_by: string
  reviewed_by: string | null
  comments: string | null
  requested_at: string
  reviewed_at: string | null
}

const recommendationColor: Record<string, string> = {
  Proceed: 'bg-green-100 text-green-700',
  Hold: 'bg-amber-100 text-amber-700',
  Reject: 'bg-red-100 text-red-700',
}

const statusColor: Record<string, string> = {
  pending: 'bg-amber-100 text-amber-700',
  approved: 'bg-blue-100 text-blue-700',
  rejected: 'bg-red-100 text-red-700',
}

const clusterLabel: Record<string, string> = {
  prod: 'Production',
  'non-prod': 'Non-Production',
  dr: 'DR',
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

export default function Dashboard() {
  const navigate = useNavigate()
  const [clusters, setClusters] = useState<ClusterSnapshot[]>([])
  const [assessments, setAssessments] = useState<Assessment[]>([])
  const [approvals, setApprovals] = useState<Approval[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAll()
  }, [])

  const fetchAll = async () => {
    try {
      setLoading(true)
      const [snapshotRes, capacityRes, assessmentRes, approvalRes] = await Promise.all([
        licenseAPI.getSnapshots(),
        licenseAPI.getCapacity(),
        assessmentAPI.getAll(),
        approvalAPI.getAll(),
      ])

      // Build capacity map
      const capacityMap: Record<string, number> = {}
      capacityRes.data.forEach((c: { environment: string; total_licensed_vpc: number }) => {
        capacityMap[c.environment] = c.total_licensed_vpc
      })

      // Group flat snapshots by cluster
      const raw: LicenseSnapshot[] = snapshotRes.data
      const grouped: Record<string, ClusterSnapshot> = {}

      raw.forEach(item => {
        if (!grouped[item.cluster]) {
          grouped[item.cluster] = {
            cluster: item.cluster,
            total_vpcs: 0,
            limit_vpcs: capacityMap[item.cluster] || 0,
            last_updated: item.collected_at,
            products: [],
          }
        }
        grouped[item.cluster].total_vpcs += item.converted_quantity
        grouped[item.cluster].products.push({
          product_name: item.product_name,
          converted_quantity: item.converted_quantity,
        })
      })

      setClusters(Object.values(grouped))
      setAssessments(assessmentRes.data)
      setApprovals(approvalRes.data)
    } catch (err) {
      console.error('Dashboard load error:', err)
    } finally {
      setLoading(false)
    }
  }

  const totalVpcs = clusters.reduce((sum, c) => sum + c.total_vpcs, 0)
  const totalLimit = clusters.reduce((sum, c) => sum + c.limit_vpcs, 0)
  const pendingApprovals = approvals.filter(a => a.status === 'pending')
  const recentAssessments = assessments.slice(0, 5)

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="flex gap-1">
        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
      </div>
    </div>
  )

  return (
    <div className="space-y-6">

      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-4">
        <KpiCard label="Total VPCs Used" value={totalVpcs} sub="Across all 3 clusters" valueColor="text-blue-600" />
        <KpiCard label="Available Headroom" value={totalLimit - totalVpcs} sub={`Before licensed limit (${totalLimit} VPC)`} valueColor="text-green-600" />
        <KpiCard label="Pending Approvals" value={pendingApprovals.length} sub="Awaiting admin decision" valueColor="text-amber-600" />
        <KpiCard label="Total Assessments" value={assessments.length} sub="All time" />
      </div>

      {/* Cluster Cards */}
      <div className="grid grid-cols-3 gap-4">
        {clusters.map(c => {
          const pct = Math.round((c.total_vpcs / c.limit_vpcs) * 100)
          const barColor = pct >= 80 ? 'bg-red-500' : pct >= 60 ? 'bg-amber-400' : 'bg-blue-500'
          return (
            <div key={c.cluster} className="bg-white rounded-xl border border-slate-200 p-5">
              <div className="text-xs font-bold text-slate-400 uppercase tracking-wide">
                {clusterLabel[c.cluster] || c.cluster}
              </div>
              <div className="text-2xl font-extrabold text-slate-800 mt-1">
                {c.total_vpcs} <span className="text-sm font-medium text-slate-400">VPCs</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2 mt-3">
                <div className={`h-2 rounded-full ${barColor}`} style={{ width: `${pct}%` }} />
              </div>
              <div className="text-xs text-slate-400 mt-1">{pct}% of {c.limit_vpcs} VPC limit</div>
              <div className="flex flex-wrap gap-1 mt-3">
                {c.products.map(p => (
                  <span key={p.product_name} className="bg-blue-50 text-blue-700 text-xs font-bold px-2 py-0.5 rounded">
                    {p.product_name} {p.converted_quantity}
                  </span>
                ))}
              </div>
              <div className="text-xs text-slate-400 mt-2">
                Last updated: {new Date(c.last_updated).toLocaleDateString()}
              </div>
            </div>
          )
        })}
      </div>

      {/* Bottom Section */}
      <div className="grid grid-cols-2 gap-4">

        {/* Recent Assessments */}
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="text-sm font-bold text-slate-800">Recent Assessments</div>
            <button
              onClick={() => navigate('/assessments')}
              className="text-xs text-blue-600 font-semibold hover:underline"
            >
              View All
            </button>
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
                {recentAssessments.length === 0 && (
                  <tr>
                    <td colSpan={5} className="text-center text-slate-400 py-6">No assessments yet</td>
                  </tr>
                )}
                {recentAssessments.map(a => (
                  <tr
                    key={a.id}
                    className="border-b border-slate-50 hover:bg-slate-50 cursor-pointer"
                    onClick={() => navigate(`/assessment/${a.id}`)}
                  >
                    <td className="py-2 px-2 font-medium text-slate-700">{a.workload_name}</td>
                    <td className="py-2 px-2 text-slate-500">{a.product_type}</td>
                    <td className="py-2 px-2 text-slate-700 font-semibold">{a.required_vpc}</td>
                    <td className="py-2 px-2">
                      <Badge label={a.recommendation} colorClass={recommendationColor[a.recommendation] || 'bg-slate-100 text-slate-600'} />
                    </td>
                    <td className="py-2 px-2">
                      <Badge label={a.status} colorClass={statusColor[a.status] || 'bg-slate-100 text-slate-600'} />
                    </td>
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
            <button
              onClick={() => navigate('/approvals')}
              className="text-xs text-blue-600 font-semibold hover:underline"
            >
              View All
            </button>
          </div>
          <div className="space-y-3">
            {pendingApprovals.length === 0 && (
              <div className="text-xs text-slate-400 text-center py-6">No pending approvals</div>
            )}
            {pendingApprovals.map(a => (
              <div key={a.id} className="flex items-center gap-3 p-3 rounded-lg border border-slate-100 hover:bg-slate-50">
                <div className="flex-1">
                  <div className="text-xs font-semibold text-slate-800">Assessment #{a.assessment_id}</div>
                  <div className="text-xs text-slate-400 mt-0.5">Requested by: {a.requested_by}</div>
                  <div className="text-xs text-slate-400 mt-0.5">{new Date(a.requested_at).toLocaleDateString()}</div>
                </div>
                <button
                  onClick={() => navigate('/approvals')}
                  className="px-3 py-1.5 text-xs font-semibold border border-blue-600 text-blue-600 rounded-md hover:bg-blue-50 transition-colors"
                >
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