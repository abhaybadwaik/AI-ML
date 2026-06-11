const assessment = {
  id: 'ASS-00124',
  workloadName: 'Customer Onboarding API',
  product: 'ACE',
  cluster: 'Production',
  estimatedCpu: 2,
  goLiveDate: '01-Jul-2026',
  submittedBy: 'abhay.admin',
  submittedOn: '09-Jun-2026 14:32',
  status: 'Pending Approval',
  ratio: '1:3',
  threadFactor: 2,
  requiredVpc: 3,
  currentUsage: 37,
  projectedUsage: 40,
  availableHeadroom: 60,
  recommendation: 'Proceed',
  risk: 'Low',
  clusterBreakdown: [
    { product: 'ACE', vpcs: 12 },
    { product: 'APIC', vpcs: 18 },
    { product: 'MQ', vpcs: 1 },
    { product: 'DataPower', vpcs: 6 },
  ],
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
  'Pending Approval': 'bg-amber-100 text-amber-700',
  'Approved': 'bg-blue-100 text-blue-700',
  'Rejected': 'bg-red-100 text-red-700',
}

export default function AssessmentDetail() {
  const rec = recommendationConfig[assessment.recommendation]
  const maxVpc = Math.max(...assessment.clusterBreakdown.map(p => p.vpcs))

  return (
    <div className="space-y-4">

      {/* Top Bar */}
      <div className="flex items-center gap-3">
        <button className="text-xs text-slate-400 hover:text-slate-600 font-semibold">
          ← Back to Assessments
        </button>
        <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${statusColor[assessment.status]}`}>
          {assessment.status}
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
                  ['Workload Name', assessment.workloadName],
                  ['Product Type', assessment.product],
                  ['Target Cluster', assessment.cluster],
                  ['Estimated CPU', `${assessment.estimatedCpu} CPUs`],
                  ['Go Live Date', assessment.goLiveDate],
                  ['Submitted By', assessment.submittedBy],
                  ['Submitted On', assessment.submittedOn],
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
                ['IBM Product Ratio (ACE Prod)', assessment.ratio],
                ['Estimated CPUs', String(assessment.estimatedCpu)],
                [`Thread Factor ÷ ${assessment.threadFactor}`, String(assessment.estimatedCpu / assessment.threadFactor)],
                [`Formula: CEILING(${assessment.estimatedCpu / assessment.threadFactor} × ${assessment.ratio.split(':')[1]})`, `${assessment.requiredVpc} VPCs`],
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
        </div>

        {/* RIGHT COLUMN */}
        <div className="space-y-4">

          {/* Capacity Impact */}
          <div className="bg-white rounded-xl border border-slate-200 p-5">
            <div className="text-sm font-bold text-slate-800 mb-4">Capacity Impact — {assessment.cluster}</div>
            <div className="bg-slate-50 rounded-lg p-4 space-y-3 mb-4">
              {[
                ['Current Cluster Usage', `${assessment.currentUsage} VPCs`, ''],
                ['Required by This Workload', `+ ${assessment.requiredVpc} VPCs`, ''],
                ['Projected Usage After Approval', `${assessment.projectedUsage} VPCs`, ''],
                ['Available Headroom After', `${assessment.availableHeadroom} VPCs`, 'text-green-600'],
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
                style={{ width: `${(assessment.projectedUsage / 100) * 100}%` }}
              />
            </div>
            <div className="text-xs text-slate-400 mt-1">
              Projected: {assessment.projectedUsage} / 100 VPCs ({assessment.projectedUsage}% of licensed capacity)
            </div>
          </div>

          {/* Cluster Breakdown Bar Chart */}
          <div className="bg-white rounded-xl border border-slate-200 p-5">
            <div className="text-sm font-bold text-slate-800 mb-4">Current Cluster Breakdown</div>
            <div className="space-y-3">
              {assessment.clusterBreakdown.map(p => (
                <div key={p.product} className="flex items-center gap-3">
                  <div className="text-xs text-slate-400 w-20 text-right">{p.product}</div>
                  <div className="flex-1 bg-slate-100 rounded-full h-6 overflow-hidden">
                    <div
                      className="h-6 rounded-full bg-blue-500 flex items-center px-3"
                      style={{ width: `${(p.vpcs / maxVpc) * 100}%` }}
                    >
                      <span className="text-white text-xs font-bold">{p.vpcs} VPC</span>
                    </div>
                  </div>
                </div>
              ))}
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
            <span className={`px-3 py-1 rounded-full text-xs font-bold ${riskColor[assessment.risk]}`}>
              Risk: {assessment.risk}
            </span>
          </div>

        </div>
      </div>
    </div>
  )
}