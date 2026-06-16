import { useState, useEffect } from 'react'
import api from '../services/api'

interface Product {
  product_name: string
  ratio: string
  measured_quantity: number
  converted_quantity: number
}

interface ClusterSnapshot {
  id: number
  cluster: string
  total_vpcs: number
  limit_vpcs: number
  last_updated: string
  source: string
  products: Product[]
}

const clusterKeys = ['prod', 'nonprod', 'dr']
const clusterLabel: Record<string, string> = {
  prod: 'Production',
  nonprod: 'Non-Production',
  dr: 'DR',
}

const barColors = ['bg-blue-500', 'bg-emerald-500', 'bg-violet-500', 'bg-orange-400']

export default function LicenseMonitoring() {
  const [snapshots, setSnapshots] = useState<ClusterSnapshot[]>([])
  const [loading, setLoading] = useState(true)
  const [activeCluster, setActiveCluster] = useState('prod')
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    fetchSnapshots()
  }, [])

  const fetchSnapshots = async () => {
    try {
      setLoading(true)
      const response = await api.get('/license-snapshots')
      setSnapshots(response.data)
    } catch (err) {
      console.error('Failed to load snapshots:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    try {
      await api.post('/ingestion-runs', {
        cluster: activeCluster,
        source_type: 'api',
      })
      await fetchSnapshots()
      alert('Refresh triggered successfully!\nPOST /ingestion-runs → status: success')
    } catch (err) {
      alert('Refresh failed. Please try again.')
    } finally {
      setRefreshing(false)
    }
  }

  const cluster = snapshots.find(s => s.cluster === activeCluster)
  const pct = cluster ? Math.round((cluster.total_vpcs / cluster.limit_vpcs) * 100) : 0
  const barColor = pct >= 80 ? 'bg-red-500' : pct >= 60 ? 'bg-amber-400' : 'bg-blue-500'
  const maxVpc = cluster ? Math.max(...cluster.products.map(p => p.converted_quantity)) : 1

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
            onClick={handleRefresh}
            disabled={refreshing}
            className="px-3 py-1.5 text-xs font-semibold bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {refreshing ? 'Refreshing...' : '↺ Refresh Now'}
          </button>
        </div>
      </div>

      {/* Cluster Tabs */}
      <div className="flex gap-1 border-b border-slate-200">
        {clusterKeys.map(key => (
          <button
            key={key}
            onClick={() => setActiveCluster(key)}
            className={`px-5 py-2 text-xs font-semibold border-b-2 transition-colors -mb-px
              ${activeCluster === key
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-slate-400 hover:text-slate-600'
              }`}
          >
            {clusterLabel[key]}
          </button>
        ))}
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center h-64">
          <div className="flex gap-1">
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
        </div>
      )}

      {!loading && cluster && (
        <div className="grid grid-cols-2 gap-4 items-start">

          {/* Left */}
          <div className="space-y-4">

            {/* Summary Card */}
            <div className="bg-white rounded-xl border border-slate-200 p-5">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-xs font-bold text-slate-400 uppercase tracking-wide">Total VPCs Used</div>
                  <div className="text-3xl font-extrabold text-blue-600 mt-1">{cluster.total_vpcs}</div>
                </div>
                <div>
                  <div className="text-xs font-bold text-slate-400 uppercase tracking-wide">Last Collected</div>
                  <div className="text-sm font-bold text-slate-800 mt-1">{cluster.last_updated}</div>
                </div>
                <div>
                  <div className="text-xs font-bold text-slate-400 uppercase tracking-wide">Data Source</div>
                  <span className="inline-block mt-1 bg-blue-100 text-blue-700 text-xs font-bold px-2 py-0.5 rounded">
                    {cluster.source}
                  </span>
                </div>
                <div>
                  <div className="text-xs font-bold text-slate-400 uppercase tracking-wide">Limit</div>
                  <div className="text-sm font-bold text-slate-800 mt-1">{cluster.limit_vpcs} VPCs</div>
                </div>
              </div>
              <div className="mt-4">
                <div className="w-full bg-slate-100 rounded-full h-2.5">
                  <div className={`h-2.5 rounded-full ${barColor}`} style={{ width: `${pct}%` }} />
                </div>
                <div className="text-xs text-slate-400 mt-1">{pct}% of {cluster.limit_vpcs} VPC limit</div>
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
                      <tr key={p.product_name} className="border-b border-slate-50 hover:bg-slate-50">
                        <td className="py-2 px-3 font-semibold text-slate-800">{p.product_name}</td>
                        <td className="py-2 px-3 text-blue-600 font-bold">{p.ratio}</td>
                        <td className="py-2 px-3 text-slate-600">{p.measured_quantity}</td>
                        <td className="py-2 px-3 font-bold text-slate-800">{p.converted_quantity}</td>
                        <td className="py-2 px-3 text-slate-600">{p.converted_quantity}</td>
                        <td className="py-2 px-3">
                          <span className="bg-green-100 text-green-700 text-xs font-bold px-2 py-0.5 rounded-full">✓ Yes</span>
                        </td>
                      </tr>
                    ))}
                    <tr className="bg-slate-50 font-bold">
                      <td className="py-2 px-3 text-slate-800">Total</td>
                      <td className="py-2 px-3">—</td>
                      <td className="py-2 px-3 text-slate-800">{cluster.products.reduce((s, p) => s + p.measured_quantity, 0)}</td>
                      <td className="py-2 px-3 text-slate-800">{cluster.total_vpcs}</td>
                      <td className="py-2 px-3 text-slate-800">{cluster.total_vpcs}</td>
                      <td className="py-2 px-3"><span className="bg-green-100 text-green-700 text-xs font-bold px-2 py-0.5 rounded-full">✓</span></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Right */}
          <div className="space-y-4">

            {/* Bar Chart */}
            <div className="bg-white rounded-xl border border-slate-200 p-5">
              <div className="text-sm font-bold text-slate-800 mb-4">
                VPC Usage by Product — {clusterLabel[activeCluster]}
              </div>
              <div className="space-y-4">
                {cluster.products.map((p, i) => (
                  <div key={p.product_name} className="flex items-center gap-3">
                    <div className="text-xs text-slate-400 w-24 text-right flex-shrink-0">{p.product_name}</div>
                    <div className="flex-1 bg-slate-100 rounded-full h-7 overflow-hidden">
                      <div
                        className={`h-7 rounded-full ${barColors[i % barColors.length]} flex items-center px-3 transition-all duration-500`}
                        style={{ width: `${Math.max((p.converted_quantity / maxVpc) * 100, 8)}%` }}
                      >
                        <span className="text-white text-xs font-bold">{p.converted_quantity} VPCs</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Info Card */}
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-5">
              <div className="text-xs font-bold text-blue-700 mb-3">📊 Cluster Summary</div>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-slate-500">Cluster</span>
                  <span className="font-bold text-slate-800">{clusterLabel[activeCluster]}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Total VPCs Used</span>
                  <span className="font-bold text-blue-600">{cluster.total_vpcs}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Available</span>
                  <span className="font-bold text-green-600">{cluster.limit_vpcs - cluster.total_vpcs}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Utilization</span>
                  <span className={`font-bold ${pct >= 80 ? 'text-red-600' : pct >= 60 ? 'text-amber-600' : 'text-green-600'}`}>{pct}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Products Running</span>
                  <span className="font-bold text-slate-800">{cluster.products.length}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}