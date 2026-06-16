import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../services/api'
import AIAssessmentSummary from '../components/ui/AIAssessmentSummary'

interface Assessment {
  id: string
  workload_name: string
  product_type: string
  cluster: string
  estimated_cpu: number
  go_live_date: string
  submitted_by: string
  submitted_on: string
  status: string
  ratio: string
  required_vpc: number
  current_usage: number
  projected_usage: number
  available_headroom: number
  recommendation: string
  risk_level: string
}

const recommendationConfig: Record<string, { bg: string; border: string; text: string; icon: string; desc: string }> = {
  Proceed: {
    bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-700',
    icon: '✅', desc: 'Sufficient headroom available. Safe to approve this workload.',
  },
  Hold: {
    bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700',
    icon: '⚠️', desc: 'Review carefully before approving. Capacity is getting tight.',
  },
  Reject: {
    bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-700',
    icon: '❌', desc: 'Approving would exceed licensed capacity. Cannot proceed.',
  },
}

const riskColor: Record<string, string> = {
  Low: 'bg-green-100 text-green-700',
  Medium: 'bg-amber-100 text-amber-700',
  High: 'bg-red-100 text-red-700',
  Critical: 'bg-red-200 text-red-800',
}

const statusColor: Record<string, string> = {
  pending_approval: 'bg-amber-100 text-amber-700',
  approved: 'bg-blue-100 text-blue-700',
  rejected: 'bg-red-100 text-red-700',
}

const statusLabel: Record<string, string> = {
  pending_approval: 'Pending Approval',
  approved: 'Approved',
  rejected: 'Rejected',
}

export default function AssessmentDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [assessment, setAssessment] = useState<Assessment | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchAssessment()
  }, [id])

  const fetchAssessment = async () => {
    try {
      setLoading(true)
      setError('')
      const response = await api.get(`/assessments/${id}`)
      setAssessment(response.data)
    } catch (err) {
      setError('Failed to load assessment details.')
    } finally {
      setLoading(false)
    }
  }

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="flex gap-1">
        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
      </div>
    </div>
  )

  if (error) return (
    <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-600 font-semibold">
      {error} <button onClick={fetchAssessment} className="ml-3 underline">Retry</button>
    </div>
  )

  if (!assessment) return null

  const rec = recommendationConfig[assessment.recommendation] || recommendationConfig['Hold']
  const threadFactor = 2
  const adjCpu = assessment.estimated_cpu / threadFactor

  return (
    <div className="space-y-4">

      {/* Top Bar */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => navigate('/assessments')}
          className="text-xs text-slate-400 hover:text-slate-600 font-semibold"
        >
          ← Back to Assessments
        </button>
        <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${statusColor[assessment.status] || 'bg-slate-100 text-slate-500'}`}>
          {statusLabel[assessment.status] || assessment.status}
        </span>
        <span className="bg-slate-100 text-slate-500 text-xs font-bold px-2 py-0.5 rounded">
          {assessment.id}
        </span>
        <div className="ml-auto flex gap-2">
          <button className="px-3 py-1.5 text-xs font-semibold border border-slate-200 text-slate-600 rounded-lg hover:bg-slate-50">
            Download PDF
          </button>
          <button className="px-3 py-1.5 text-xs font-semibold bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            Submit for Approval →
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 items-start">

        {/* LEFT COLUMN */}
        <div className="space-y-4">

          {/* Request Summary */}
          <div className="bg-white rounded-xl border border-slate-200 p-5">
            <div className="text-sm font-bold text-slate-800 mb-4">Request Summary</div>
            <table className="w-full text-xs">
              <tbody>
                {[
                  ['Workload Name', assessment.workload_name],
                  ['Product Type', assessment.product_type],
                  ['Target Cluster', assessment.cluster],
                  ['Estimated CPU', `${assessment.estimated_cpu} CPUs`],
                  ['Go Live Date', assessment.go_live_date],
                  ['Submitted By', assessment.submitted_by],
                  ['Submitted On', assessment.submitted_on],
                ].map(([label, value]) => (
                  <tr key={label} className="border-b border-slate-50">
                    <td className="py-2 pr-4 text-slate-400 font-medium w-36">{label}</td>
                    <td className="py-2 text-slate-800 font-semibold">{value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* VPC Calculation */}
          <div className="bg-white rounded-xl border border-slate-200 p-5">
            <div className="text-sm font-bold text-slate-800 mb-4">VPC Calculation Breakdown</div>
            <div className="bg-slate-50 rounded-lg p-4 space-y-3">
              {[
                ['IBM Product Ratio', assessment.ratio],
                ['Estimated CPUs', String(assessment.estimated_cpu)],
                [`Thread Factor ÷ ${threadFactor}`, String(adjCpu)],
                [`Formula: CEILING(${adjCpu} × ${assessment.ratio?.split(':')[1]})`, `${assessment.required_vpc} VPCs`],
              ].map(([label, value], i, arr) => (
                <div
                  key={label}
                  className={`flex justify-between items-center pb-3 ${i < arr.length - 1 ? 'border-b border-slate-200' : ''}`}
                >
                  <span className={`text-xs ${i === arr.length - 1 ? 'font-bold text-slate-800' : 'text-slate-500'}`}>
                    {label}
                  </span>
                  <span className={`text-sm font-bold ${i === arr.length - 1 ? 'text-blue-600 text-base' : 'text-slate-800'}`}>
                    {value}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* AI Summary */}
          <AIAssessmentSummary
            assessment={{
              workloadName: assessment.workload_name,
              product: assessment.product_type,
              cluster: assessment.cluster,
              estimatedCpu: assessment.estimated_cpu,
              requiredVpc: assessment.required_vpc,
              currentUsage: assessment.current_usage,
              projectedUsage: assessment.projected_usage,
              availableHeadroom: assessment.available_headroom,
              recommendation: assessment.recommendation,
              risk: assessment.risk_level,
            }}
          />
        </div>

        {/* RIGHT COLUMN */}
        <div className="space-y-4">

          {/* Capacity Impact */}
          <div className="bg-white rounded-xl border border-slate-200 p-5">
            <div className="text-sm font-bold text-slate-800 mb-4">Capacity Impact — {assessment.cluster}</div>
            <div className="bg-slate-50 rounded-lg p-4 space-y-3 mb-4">
              {[
                ['Current Cluster Usage', `${assessment.current_usage} VPCs`, ''],
                ['Required by This Workload', `+ ${assessment.required_vpc} VPCs`, ''],
                ['Projected Usage After Approval', `${assessment.projected_usage} VPCs`, ''],
                ['Available Headroom After', `${assessment.available_headroom} VPCs`, 'text-green-600'],
              ].map(([label, value, extra], i, arr) => (
                <div
                  key={label}
                  className={`flex justify-between items-center pb-3 ${i < arr.length - 1 ? 'border-b border-slate-200' : ''}`}
                >
                  <span className="text-xs text-slate-500">{label}</span>
                  <span className={`text-sm font-bold ${extra || 'text-slate-800'}`}>{value}</span>
                </div>
              ))}
            </div>
            <div className="w-full bg-slate-100 rounded-full h-3">
              <div
                className="h-3 rounded-full bg-amber-400"
                style={{ width: `${Math.min((assessment.projected_usage / 100) * 100, 100)}%` }}
              />
            </div>
            <div className="text-xs text-slate-400 mt-1">
              Projected: {assessment.projected_usage} / 100 VPCs
            </div>
          </div>

          {/* Recommendation Box */}
          <div className={`rounded-xl border-2 p-5 flex items-center gap-4 ${rec.bg} ${rec.border}`}>
            <div className="text-3xl">{rec.icon}</div>
            <div className="flex-1">
              <div className={`text-xs font-bold uppercase tracking-wider ${rec.text}`}>
                Engine Recommendation
              </div>
              <div className={`text-xl font-extrabold mt-1 ${rec.text}`}>
                {assessment.recommendation}
              </div>
              <div className={`text-xs mt-1 ${rec.text}`}>{rec.desc}</div>
            </div>
            <span className={`px-3 py-1 rounded-full text-xs font-bold ${riskColor[assessment.risk_level] || 'bg-slate-100 text-slate-600'}`}>
              Risk: {assessment.risk_level}
            </span>
          </div>

        </div>
      </div>
    </div>
  )
}