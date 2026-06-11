import { useState } from 'react'

const clusterData = {
  prod: {
    label: 'Production',
    totalVpcs: 37,
    limit: 50,
    lastCollected: '01-Jun-2026 10:03',
    source: 'API',
    ibmVersion: '4.2.3',
    products: [
      { name: 'ACE', ratio: '1:3', measuredVcpus: 4, calculatedVpcs: 12, ibmVpcs: 12 },
      { name: 'MQ Advanced', ratio: '2:1', measuredVcpus: 2, calculatedVpcs: 1, ibmVpcs: 1 },
      { name: 'API Connect', ratio: '1:1', measuredVcpus: 18, calculatedVpcs: 18, ibmVpcs: 18 },
      { name: 'DataPower', ratio: '1:1', measuredVcpus: 6, calculatedVpcs: 6, ibmVpcs: 6 },
    ],
    history: [
      { date: '01-Jun-2026', source: 'API', totalVpcs: 37, status: 'Success' },
      { date: '25-May-2026', source: 'PDF', totalVpcs: 35, status: 'Success' },
      { date: '18-May-2026', source: 'API', totalVpcs: 35, status: 'Success' },
      { date: '10-May-2026', source: 'API', totalVpcs: 32, status: 'Failed' },
    ],
  },
  nonprod: {
    label: 'Non-Production',
    totalVpcs: 13,
    limit: 50,
    lastCollected: '01-Jun-2026 10:05',
    source: 'API',
    ibmVersion: '4.2.3',
    products: [
      { name: 'ACE', ratio: '2:3', measuredVcpus: 12, calculatedVpcs: 6, ibmVpcs: 6 },
      { name: 'MQ Advanced', ratio: '4:1', measuredVcpus: 8, calculatedVpcs: 2, ibmVpcs: 2 },
      { name: 'API Connect', ratio: '2:1', measuredVcpus: 6, calculatedVpcs: 3, ibmVpcs: 3 },
      { name: 'DataPower', ratio: '2:1', measuredVcpus: 2, calculatedVpcs: 1, ibmVpcs: 1 },
    ],
    history: [
      { date: '01-Jun-2026', source: 'API', totalVpcs: 13, status: 'Success' },
      { date: '25-May-2026', source: 'API', totalVpcs: 12, status: 'Success' },
      { date: '18-May-2026', source: 'PDF', totalVpcs: 11, status: 'Success' },
      { date: '10-May-2026', source: 'API', totalVpcs: 11, status: 'Success' },
    ],
  },
  dr: {
    label: 'DR',
    totalVpcs: 25,
    limit: 50,
    lastCollected: '01-Jun-2026 10:08',
    source: 'PDF',
    ibmVersion: '4.2.3',
    products: [
      { name: 'MQ Advanced', ratio: '2:1', measuredVcpus: 2, calculatedVpcs: 2, ibmVpcs: 2 },
      { name: 'API Connect', ratio: '1:1', measuredVcpus: 18, calculatedVpcs: 18, ibmVpcs: 18 },
      { name: 'DataPower', ratio: '1:1', measuredVcpus: 6, calculatedVpcs: 6, ibmVpcs: 6 },
    ],
    history: [
      { date: '01-Jun-2026', source: 'PDF', totalVpcs: 25, status: 'Success' },
      { date: '25-May-2026', source: 'PDF', totalVpcs: 25, status: 'Success' },
      { date: '18-May-2026', source: 'API', totalVpcs: 24, status: 'Success' },
      { date: '10-May-2026', source: 'API', totalVpcs: 24, status: 'Failed' },
    ],
  },
}

type ClusterKey = keyof typeof clusterData

export default function LicenseMonitoring() {
  const [activeCluster, setActiveCluster] = useState<ClusterKey>('prod')
  const cluster = clusterData[activeCluster]
  const pct = Math.round((cluster.totalVpcs / cluster.limit) * 100)
  const barColor = pct >= 80 ? 'bg-red-500' : pct >= 60 ? 'bg-amber-400' : 'bg-blue-500'
  const maxVpc = Math.max(...cluster.products.map(p => p.calculatedVpcs))

  const barColors = ['bg-blue-500', 'bg-emerald-500', 'bg-violet-500', 'bg-orange-400']

  return (
    <div className="space-y-4">

      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="text-sm font-bold text-slate-800">License Monitoring</div>
        <div className="ml-auto flex gap-2">
          <button className="px-3 py-1.5 text-xs font-semibold border border-slate-200 text-slate-600 rounded-lg hover:bg-slate-50">
            ↑ Upload PDF
          </button>
          <button
            onClick={() => alert('Refresh triggered!\nPOST /ingestion-runs\n\nStatus: pending → success')}
            className="px-3 py-1.5 text-xs font-semibold bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            ↺ Refresh Now
          </button>
        </div>
      </div>

      {/* Cluster Tabs */}
      <div className="flex gap-1 border-b border-slate-200">
        {(Object.keys(clusterData) as ClusterKey[]).map(key => (
          <button
            key={key}
            onClick={() => setActiveCluster(key)}
            className={`px-5 py-2 text-xs font-semibold border-b-2 transition-colors -mb-px
              ${activeCluster === key
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-slate-400 hover:text-slate-600'
              }`}
          >
            {clusterData[key].label}
          </button>
        ))}
      </div>

      {/* Summary + Chart Row */}
      <div className="grid grid-cols-2 gap-4 items-start">

        {/* Left — Summary + Table */}
        <div className="space-y-4">

          {/* Cluster Summary Card */}
          <div className="bg-white rounded-xl border border-slate-200 p-5">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-xs font-bold text-slate-400 uppercase tracking-wide">Total VPCs Used</div>
                <div className="text-3xl font-extrabold text-blue-600 mt-1">{cluster.totalVpcs}</div>
              </div>
              <div>
                <div className="text-xs font-bold text-slate-400 uppercase tracking-wide">Last Collected</div>
                <div className="text-sm font-bold text-slate-800 mt-1">{cluster.lastCollected}</div>
              </div>
              <div>
                <div className="text-xs font-bold text-slate-400 uppercase tracking-wide">Data Source</div>
                <span className="inline-block mt-1 bg-blue-100 text-blue-700 text-xs font-bold px-2 py-0.5 rounded">
                  {cluster.source}
                </span>
              </div>
              <div>
                <div className="text-xs font-bold text-slate-400 uppercase tracking-wide">IBM License Svc</div>
                <div className="text-sm font-bold text-slate-800 mt-1">v{cluster.ibmVersion}</div>
              </div>
            </div>
            <div className="mt-4">
              <div className="w-full bg-slate-100 rounded-full h-2.5">
                <div className={`h-2.5 rounded-full ${barColor}`} style={{ width: `${pct}%` }} />
              </div>
              <div className="text-xs text-slate-400 mt-1">{pct}% of {cluster.limit} VPC limit</div>
            </div>
          </div>

          {/* Product Breakdown Table */}
          <div className="bg-white rounded-xl border border-slate-200 p-5">
            <div className="text-sm font-bold text-slate-800 mb-4">Product Breakdown</div>
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-slate-100">
                    {['Product', 'Ratio', 'vCPUs', 'Calc VPCs', 'IBM VPCs', 'Match'].map(h => (
                      <th key={h} className="text-left py-2 px-3 text-slate-400 font-bold uppercase tracking-wide">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {cluster.products.map(p => (
                    <tr key={p.name} className="border-b border-slate-50 hover:bg-slate-50">
                      <td className="py-2 px-3 font-semibold text-slate-800">{p.name}</td>
                      <td className="py-2 px-3 text-blue-600 font-bold">{p.ratio}</td>
                      <td className="py-2 px-3 text-slate-600">{p.measuredVcpus}</td>
                      <td className="py-2 px-3 font-bold text-slate-800">{p.calculatedVpcs}</td>
                      <td className="py-2 px-3 text-slate-600">{p.ibmVpcs}</td>
                      <td className="py-2 px-3">
                        {p.calculatedVpcs === p.ibmVpcs ? (
                          <span className="bg-green-100 text-green-700 text-xs font-bold px-2 py-0.5 rounded-full">✓ Yes</span>
                        ) : (
                          <span className="bg-red-100 text-red-700 text-xs font-bold px-2 py-0.5 rounded-full">✗ No</span>
                        )}
                      </td>
                    </tr>
                  ))}
                  <tr className="bg-slate-50 font-bold">
                    <td className="py-2 px-3 text-slate-800">Total</td>
                    <td className="py-2 px-3">—</td>
                    <td className="py-2 px-3 text-slate-800">{cluster.products.reduce((s, p) => s + p.measuredVcpus, 0)}</td>
                    <td className="py-2 px-3 text-slate-800">{cluster.totalVpcs}</td>
                    <td className="py-2 px-3 text-slate-800">{cluster.totalVpcs}</td>
                    <td className="py-2 px-3"><span className="bg-green-100 text-green-700 text-xs font-bold px-2 py-0.5 rounded-full">✓</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Right — Bar Chart + History */}
        <div className="space-y-4">

          {/* Bar Chart */}
          <div className="bg-white rounded-xl border border-slate-200 p-5">
            <div className="text-sm font-bold text-slate-800 mb-4">
              VPC Usage by Product — {cluster.label}
            </div>
            <div className="space-y-4">
              {cluster.products.map((p, i) => (
                <div key={p.name} className="flex items-center gap-3">
                  <div className="text-xs text-slate-400 w-24 text-right flex-shrink-0">{p.name}</div>
                  <div className="flex-1 bg-slate-100 rounded-full h-7 overflow-hidden">
                    <div
                      className={`h-7 rounded-full ${barColors[i % barColors.length]} flex items-center px-3 transition-all duration-500`}
                      style={{ width: `${Math.max((p.calculatedVpcs / maxVpc) * 100, 8)}%` }}
                    >
                      <span className="text-white text-xs font-bold">{p.calculatedVpcs} VPCs</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* History Table */}
          <div className="bg-white rounded-xl border border-slate-200 p-5">
            <div className="text-sm font-bold text-slate-800 mb-4">Collection History</div>
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-slate-100">
                  {['Date', 'Source', 'Total VPCs', 'Status', ''].map(h => (
                    <th key={h} className="text-left py-2 px-3 text-slate-400 font-bold uppercase tracking-wide">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {cluster.history.map((h, i) => (
                  <tr key={i} className="border-b border-slate-50 hover:bg-slate-50">
                    <td className="py-2 px-3 text-slate-600">{h.date}</td>
                    <td className="py-2 px-3">
                      <span className="bg-slate-100 text-slate-500 text-xs font-bold px-2 py-0.5 rounded">{h.source}</span>
                    </td>
                    <td className="py-2 px-3 font-bold text-slate-800">{h.totalVpcs}</td>
                    <td className="py-2 px-3">
                      <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${h.status === 'Success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                        {h.status}
                      </span>
                    </td>
                    <td className="py-2 px-3">
                      <button className="text-xs text-blue-600 font-semibold hover:underline">View</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

        </div>
      </div>
    </div>
  )
}
