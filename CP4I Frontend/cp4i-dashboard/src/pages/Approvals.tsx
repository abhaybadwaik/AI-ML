import { useState } from 'react'

const pendingApprovals = [
  {
    id: 'APP-001', assessmentId: 'ASS-00124', workload: 'Customer Onboarding API',
    submittedBy: 'abhay.admin', product: 'ACE', cluster: 'Production',
    requiredVpc: 3, projectedUsage: 40, risk: 'Low', recommendation: 'Proceed', submittedDate: '09-Jun-2026',
  },
  {
    id: 'APP-002', assessmentId: 'ASS-00125', workload: 'API Gateway v2',
    submittedBy: 'sumith.ops', product: 'DataPower', cluster: 'DR',
    requiredVpc: 3, projectedUsage: 28, risk: 'Low', recommendation: 'Proceed', submittedDate: '08-Jun-2026',
  },
  {
    id: 'APP-003', assessmentId: 'ASS-00126', workload: 'KYC Verification Service',
    submittedBy: 'pratik.eng', product: 'APIC', cluster: 'Production',
    requiredVpc: 15, projectedUsage: 52, risk: 'High', recommendation: 'Hold', submittedDate: '07-Jun-2026',
  },
]

const approvalHistory = [
  { id: 'APP-H01', workload: 'Payment Gateway', decision: 'Approved', decidedBy: 'admin.bank', comments: 'Capacity sufficient, proceed.', date: '05-Jun-2026' },
  { id: 'APP-H02', workload: 'Fraud Detection MQ', decision: 'Approved', decidedBy: 'admin.bank', comments: 'Low risk, approved.', date: '03-Jun-2026' },
  { id: 'APP-H03', workload: 'DataSync Batch Job', decision: 'Rejected', decidedBy: 'admin.bank', comments: 'Exceeds licensed capacity.', date: '01-Jun-2026' },
  { id: 'APP-H04', workload: 'Reporting Service', decision: 'Approved', decidedBy: 'admin.bank', comments: 'Approved for non-prod only.', date: '28-May-2026' },
]

const riskColor: Record<string, string> = {
  Low: 'bg-green-100 text-green-700',
  Medium: 'bg-amber-100 text-amber-700',
  High: 'bg-red-100 text-red-700',
  Critical: 'bg-red-200 text-red-800',
}

const recommendationColor: Record<string, string> = {
  Proceed: 'bg-green-100 text-green-700',
  Hold: 'bg-amber-100 text-amber-700',
  Reject: 'bg-red-100 text-red-700',
}

function Badge({ label, colorClass }: { label: string; colorClass: string }) {
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${colorClass}`}>
      {label}
    </span>
  )
}

export default function Approvals() {
  const [activeTab, setActiveTab] = useState('pending')
  const [selectedApproval, setSelectedApproval] = useState<typeof pendingApprovals[0] | null>(null)
  const [comments, setComments] = useState('')
  const [actionDone, setActionDone] = useState<Record<string, string>>({})

  const tabs = [
    { key: 'pending', label: `Pending (${pendingApprovals.length})` },
    { key: 'approved', label: 'Approved (12)' },
    { key: 'rejected', label: 'Rejected (4)' },
    { key: 'all', label: 'All' },
  ]

  const handleAction = (action: 'approve' | 'reject') => {
    if (!selectedApproval) return
    setActionDone(prev => ({ ...prev, [selectedApproval.id]: action }))
    setSelectedApproval(null)
    setComments('')
    alert(`✓ ${action === 'approve' ? 'Approved' : 'Rejected'}!\n\nPATCH /approvals/${selectedApproval.id}\nEmail notification sent to ${selectedApproval.submittedBy}`)
  }

  return (
    <div className="space-y-4">

      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="text-sm font-bold text-slate-800">Approval Queue</div>
        <span className="bg-amber-100 text-amber-700 text-xs font-bold px-2 py-0.5 rounded-full">
          {pendingApprovals.length} Pending
        </span>
        <div className="ml-auto flex gap-2">
          <button className="px-3 py-1.5 text-xs font-semibold border border-slate-200 text-slate-600 rounded-lg hover:bg-slate-50">
            Filter by Cluster
          </button>
          <button className="px-3 py-1.5 text-xs font-semibold border border-slate-200 text-slate-600 rounded-lg hover:bg-slate-50">
            Export to Excel
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-slate-200">
        {tabs.map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2 text-xs font-semibold border-b-2 transition-colors -mb-px
              ${activeTab === tab.key
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-slate-400 hover:text-slate-600'
              }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Pending Table */}
      <div className="bg-white rounded-xl border border-slate-200">
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-slate-100">
                {['Workload Name', 'Submitted By', 'Product', 'Cluster', 'Req. VPCs', 'Projected', 'Risk', 'Recommendation', 'Submitted', 'Action'].map(h => (
                  <th key={h} className="text-left py-3 px-4 text-slate-400 font-bold uppercase tracking-wide whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {pendingApprovals.map(a => (
                <tr key={a.id} className={`border-b border-slate-50 hover:bg-slate-50 ${actionDone[a.id] ? 'opacity-40' : ''}`}>
                  <td className="py-3 px-4 font-semibold text-slate-800">{a.workload}</td>
                  <td className="py-3 px-4 text-slate-500">{a.submittedBy}</td>
                  <td className="py-3 px-4 text-slate-500">{a.product}</td>
                  <td className="py-3 px-4 text-slate-500">{a.cluster}</td>
                  <td className="py-3 px-4 font-bold text-slate-800">{a.requiredVpc}</td>
                  <td className="py-3 px-4 font-bold text-slate-800">{a.projectedUsage}</td>
                  <td className="py-3 px-4"><Badge label={a.risk} colorClass={riskColor[a.risk]} /></td>
                  <td className="py-3 px-4"><Badge label={a.recommendation} colorClass={recommendationColor[a.recommendation]} /></td>
                  <td className="py-3 px-4 text-slate-400">{a.submittedDate}</td>
                  <td className="py-3 px-4">
                    {actionDone[a.id] ? (
                      <span className={`text-xs font-bold ${actionDone[a.id] === 'approve' ? 'text-green-600' : 'text-red-600'}`}>
                        {actionDone[a.id] === 'approve' ? '✓ Approved' : '✗ Rejected'}
                      </span>
                    ) : (
                      <button
                        onClick={() => setSelectedApproval(a)}
                        className="px-3 py-1.5 bg-blue-600 text-white text-xs font-bold rounded-lg hover:bg-blue-700 transition-colors"
                      >
                        Review
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* History Table */}
      <div className="bg-white rounded-xl border border-slate-200 p-5">
        <div className="text-sm font-bold text-slate-800 mb-4">Approval History</div>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-slate-100">
                {['Workload Name', 'Decision', 'Decided By', 'Comments', 'Decision Date', ''].map(h => (
                  <th key={h} className="text-left py-3 px-4 text-slate-400 font-bold uppercase tracking-wide">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {approvalHistory.map(h => (
                <tr key={h.id} className="border-b border-slate-50 hover:bg-slate-50">
                  <td className="py-3 px-4 font-semibold text-slate-800">{h.workload}</td>
                  <td className="py-3 px-4">
                    <Badge
                      label={h.decision}
                      colorClass={h.decision === 'Approved' ? 'bg-blue-100 text-blue-700' : 'bg-red-100 text-red-700'}
                    />
                  </td>
                  <td className="py-3 px-4 text-slate-500">{h.decidedBy}</td>
                  <td className="py-3 px-4 text-slate-500">{h.comments}</td>
                  <td className="py-3 px-4 text-slate-400">{h.date}</td>
                  <td className="py-3 px-4">
                    <button className="text-xs text-blue-600 font-semibold hover:underline">View</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Slide Panel Overlay */}
      {selectedApproval && (
        <>
          <div
            className="fixed inset-0 bg-black/20 z-40"
            onClick={() => setSelectedApproval(null)}
          />
          <div className="fixed right-0 top-0 bottom-0 w-96 bg-white border-l border-slate-200 z-50 overflow-y-auto shadow-2xl">
            <div className="p-6 space-y-4">

              {/* Panel Header */}
              <div className="flex items-center justify-between">
                <div className="text-sm font-bold text-slate-800">Assessment Review</div>
                <button
                  onClick={() => setSelectedApproval(null)}
                  className="text-slate-400 hover:text-slate-600 font-bold text-lg"
                >
                  ✕
                </button>
              </div>
              <div className="text-xs text-slate-400">{selectedApproval.assessmentId} · {selectedApproval.workload}</div>

              {/* Summary */}
              <div className="bg-slate-50 rounded-lg p-4 space-y-3">
                {[
                  ['Product', selectedApproval.product],
                  ['Cluster', selectedApproval.cluster],
                  ['Required VPCs', String(selectedApproval.requiredVpc)],
                  ['Projected Usage', `${selectedApproval.projectedUsage} VPCs`],
                  ['Recommendation', selectedApproval.recommendation],
                  ['Risk Level', selectedApproval.risk],
                ].map(([label, value]) => (
                  <div key={label} className="flex justify-between items-center pb-2 border-b border-slate-200 last:border-0">
                    <span className="text-xs text-slate-500">{label}</span>
                    <span className="text-xs font-bold text-slate-800">{value}</span>
                  </div>
                ))}
              </div>

              {/* Comments */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-2">
                  Approver Comments
                </label>
                <textarea
                  value={comments}
                  onChange={e => setComments(e.target.value)}
                  rows={3}
                  className="w-full border border-slate-200 rounded-lg px-3 py-2 text-xs outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 resize-none"
                  placeholder="Add your notes or reason for decision..."
                />
              </div>

              {/* Action Buttons */}
              <div className="flex gap-2">
                <button
                  onClick={() => handleAction('approve')}
                  className="flex-1 py-2.5 bg-green-600 text-white text-xs font-bold rounded-lg hover:bg-green-700 transition-colors"
                >
                  ✓ Approve
                </button>
                <button
                  onClick={() => handleAction('reject')}
                  className="flex-1 py-2.5 bg-red-600 text-white text-xs font-bold rounded-lg hover:bg-red-700 transition-colors"
                >
                  ✗ Reject
                </button>
              </div>
              <button className="w-full py-2 border border-slate-200 text-slate-500 text-xs font-semibold rounded-lg hover:bg-slate-50 transition-colors">
                📧 Request More Info
              </button>

            </div>
          </div>
        </>
      )}

    </div>
  )
}