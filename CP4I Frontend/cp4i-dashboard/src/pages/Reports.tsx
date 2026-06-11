import { useState } from 'react'

const licenseData = [
  { date: '01-Jun-2026', cluster: 'Production', product: 'ACE', vcpus: 4, vpcs: 12, source: 'API' },
  { date: '01-Jun-2026', cluster: 'Production', product: 'MQ Advanced', vcpus: 2, vpcs: 1, source: 'API' },
  { date: '01-Jun-2026', cluster: 'Production', product: 'API Connect', vcpus: 18, vpcs: 18, source: 'API' },
  { date: '01-Jun-2026', cluster: 'Production', product: 'DataPower', vcpus: 6, vpcs: 6, source: 'API' },
  { date: '01-Jun-2026', cluster: 'Non-Prod', product: 'ACE', vcpus: 12, vpcs: 6, source: 'API' },
  { date: '01-Jun-2026', cluster: 'Non-Prod', product: 'API Connect', vcpus: 6, vpcs: 3, source: 'API' },
  { date: '01-Jun-2026', cluster: 'DR', product: 'API Connect', vcpus: 18, vpcs: 18, source: 'PDF' },
  { date: '01-Jun-2026', cluster: 'DR', product: 'DataPower', vcpus: 6, vpcs: 6, source: 'PDF' },
]

const assessmentData = [
  { date: '09-Jun-2026', workload: 'Customer Onboarding API', product: 'ACE', requiredVpc: 3, projected: 40, recommendation: 'Proceed', status: 'Pending' },
  { date: '05-Jun-2026', workload: 'Payment Gateway', product: 'APIC', requiredVpc: 12, projected: 49, recommendation: 'Hold', status: 'Approved' },
  { date: '03-Jun-2026', workload: 'Fraud Detection MQ', product: 'MQ', requiredVpc: 2, projected: 15, recommendation: 'Proceed', status: 'Approved' },
  { date: '01-Jun-2026', workload: 'DataSync Batch Job', product: 'ACE', requiredVpc: 9, projected: 46, recommendation: 'Reject', status: 'Rejected' },
  { date: '08-Jun-2026', workload: 'API Gateway v2', product: 'DataPower', requiredVpc: 3, projected: 28, recommendation: 'Proceed', status: 'Pending' },
]

const approvalData = [
  { date: '05-Jun-2026', workload: 'Payment Gateway', decision: 'Approved', decidedBy: 'admin.bank', comments: 'Capacity sufficient.' },
  { date: '03-Jun-2026', workload: 'Fraud Detection MQ', decision: 'Approved', decidedBy: 'admin.bank', comments: 'Low risk.' },
  { date: '01-Jun-2026', workload: 'DataSync Batch Job', decision: 'Rejected', decidedBy: 'admin.bank', comments: 'Exceeds capacity.' },
  { date: '28-May-2026', workload: 'Reporting Service', decision: 'Approved', decidedBy: 'admin.bank', comments: 'Non-prod only.' },
]

const recommendationColor: Record<string, string> = {
  Proceed: 'bg-green-100 text-green-700',
  Hold: 'bg-amber-100 text-amber-700',
  Reject: 'bg-red-100 text-red-700',
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

export default function Reports() {
  const [reportType, setReportType] = useState('license')
  const [cluster, setCluster] = useState('all')
  const [dateFrom, setDateFrom] = useState('2026-05-01')
  const [dateTo, setDateTo] = useState('2026-06-09')
  const [format, setFormat] = useState('screen')
  const [generated, setGenerated] = useState(true)

  const handleGenerate = () => {
    setGenerated(true)
    if (format === 'pdf') {
      alert('Downloading PDF...\nGET /reports?type=' + reportType + '&format=pdf')
    } else if (format === 'excel') {
      alert('Downloading Excel...\nGET /reports?type=' + reportType + '&format=excel')
    }
  }

  return (
    <div className="space-y-4">

      {/* Filter Card */}
      <div className="bg-white rounded-xl border border-slate-200 p-5">
        <div className="text-sm font-bold text-slate-800 mb-4">Report Filters</div>
        <div className="grid grid-cols-5 gap-4 items-end">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Report Type</label>
            <select
              value={reportType}
              onChange={e => { setReportType(e.target.value); setGenerated(false) }}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-xs outline-none focus:border-blue-500"
            >
              <option value="license">License Usage</option>
              <option value="assessment">Assessment Report</option>
              <option value="approval">Approval History</option>
              <option value="consolidated">Consolidated</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Cluster</label>
            <select
              value={cluster}
              onChange={e => setCluster(e.target.value)}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-xs outline-none focus:border-blue-500"
            >
              <option value="all">All Clusters</option>
              <option value="prod">Production</option>
              <option value="nonprod">Non-Production</option>
              <option value="dr">DR</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Date From</label>
            <input
              type="date"
              value={dateFrom}
              onChange={e => setDateFrom(e.target.value)}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-xs outline-none focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Date To</label>
            <input
              type="date"
              value={dateTo}
              onChange={e => setDateTo(e.target.value)}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-xs outline-none focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Format</label>
            <select
              value={format}
              onChange={e => setFormat(e.target.value)}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-xs outline-none focus:border-blue-500"
            >
              <option value="screen">View on Screen</option>
              <option value="pdf">Download PDF</option>
              <option value="excel">Download Excel</option>
            </select>
          </div>
        </div>

        <div className="flex gap-2 mt-4">
          <button
            onClick={handleGenerate}
            className="px-4 py-2 bg-blue-600 text-white text-xs font-bold rounded-lg hover:bg-blue-700 transition-colors"
          >
            Generate Report
          </button>
          <button
            onClick={() => alert('Downloading PDF...\nGET /reports?format=pdf')}
            className="px-4 py-2 border border-slate-200 text-slate-600 text-xs font-bold rounded-lg hover:bg-slate-50 transition-colors"
          >
            Download PDF
          </button>
          <button
            onClick={() => alert('Downloading Excel...\nGET /reports?format=excel')}
            className="px-4 py-2 border border-slate-200 text-slate-600 text-xs font-bold rounded-lg hover:bg-slate-50 transition-colors"
          >
            Download Excel
          </button>
          <button
            onClick={() => { setReportType('license'); setCluster('all'); setFormat('screen'); setGenerated(false) }}
            className="px-4 py-2 text-slate-400 text-xs font-bold rounded-lg hover:bg-slate-50 transition-colors ml-auto"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {/* Report Preview */}
      {generated && (
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="text-sm font-bold text-slate-800">
              {reportType === 'license' && 'License Usage Report'}
              {reportType === 'assessment' && 'Assessment Report'}
              {reportType === 'approval' && 'Approval History Report'}
              {reportType === 'consolidated' && 'Consolidated Report'}
              {' '}— {cluster === 'all' ? 'All Clusters' : cluster} ({dateFrom} to {dateTo})
            </div>
            <span className="bg-slate-100 text-slate-500 text-xs font-bold px-2 py-0.5 rounded">
              {reportType === 'license' ? licenseData.length :
               reportType === 'assessment' ? assessmentData.length :
               approvalData.length} records
            </span>
          </div>

          {/* License Usage Table */}
          {(reportType === 'license' || reportType === 'consolidated') && (
            <div className="mb-6">
              {reportType === 'consolidated' && (
                <div className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-3">
                  License Usage
                </div>
              )}
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-slate-100">
                      {['Date', 'Cluster', 'Product', 'vCPUs', 'VPCs', 'Source'].map(h => (
                        <th key={h} className="text-left py-2 px-3 text-slate-400 font-bold uppercase tracking-wide">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {licenseData.map((r, i) => (
                      <tr key={i} className="border-b border-slate-50 hover:bg-slate-50">
                        <td className="py-2 px-3 text-slate-600">{r.date}</td>
                        <td className="py-2 px-3 text-slate-600">{r.cluster}</td>
                        <td className="py-2 px-3 font-semibold text-slate-800">{r.product}</td>
                        <td className="py-2 px-3 text-slate-600">{r.vcpus}</td>
                        <td className="py-2 px-3 font-bold text-slate-800">{r.vpcs}</td>
                        <td className="py-2 px-3">
                          <span className="bg-slate-100 text-slate-500 text-xs font-bold px-2 py-0.5 rounded">{r.source}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Assessment Table */}
          {(reportType === 'assessment' || reportType === 'consolidated') && (
            <div className="mb-6">
              {reportType === 'consolidated' && (
                <div className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-3 mt-4">
                  Assessments
                </div>
              )}
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-slate-100">
                      {['Date', 'Workload Name', 'Product', 'Req. VPC', 'Projected', 'Recommendation', 'Status'].map(h => (
                        <th key={h} className="text-left py-2 px-3 text-slate-400 font-bold uppercase tracking-wide">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {assessmentData.map((r, i) => (
                      <tr key={i} className="border-b border-slate-50 hover:bg-slate-50">
                        <td className="py-2 px-3 text-slate-600">{r.date}</td>
                        <td className="py-2 px-3 font-semibold text-slate-800">{r.workload}</td>
                        <td className="py-2 px-3 text-slate-600">{r.product}</td>
                        <td className="py-2 px-3 font-bold text-slate-800">{r.requiredVpc}</td>
                        <td className="py-2 px-3 text-slate-600">{r.projected}</td>
                        <td className="py-2 px-3"><Badge label={r.recommendation} colorClass={recommendationColor[r.recommendation]} /></td>
                        <td className="py-2 px-3"><Badge label={r.status} colorClass={statusColor[r.status]} /></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Approval Table */}
          {(reportType === 'approval' || reportType === 'consolidated') && (
            <div>
              {reportType === 'consolidated' && (
                <div className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-3 mt-4">
                  Approval History
                </div>
              )}
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-slate-100">
                      {['Date', 'Workload Name', 'Decision', 'Decided By', 'Comments'].map(h => (
                        <th key={h} className="text-left py-2 px-3 text-slate-400 font-bold uppercase tracking-wide">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {approvalData.map((r, i) => (
                      <tr key={i} className="border-b border-slate-50 hover:bg-slate-50">
                        <td className="py-2 px-3 text-slate-600">{r.date}</td>
                        <td className="py-2 px-3 font-semibold text-slate-800">{r.workload}</td>
                        <td className="py-2 px-3">
                          <Badge
                            label={r.decision}
                            colorClass={r.decision === 'Approved' ? 'bg-blue-100 text-blue-700' : 'bg-red-100 text-red-700'}
                          />
                        </td>
                        <td className="py-2 px-3 text-slate-600">{r.decidedBy}</td>
                        <td className="py-2 px-3 text-slate-500">{r.comments}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}