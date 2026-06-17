import { useState, useEffect } from 'react'
import { licenseAPI } from '../services/api'

interface Snapshot {
  id: number
  cluster: string
  product_name: string
  converted_quantity: number
  collected_at: string
}

interface Capacity {
  id: number
  environment: string
  total_licensed_vpc: number
}

interface ClusterData {
  cluster: string
  total_vpcs: number
  limit_vpcs: number
  last_updated: string
  products: { product_name: string; converted_quantity: number }[]
}

const clusterKeys = ['prod', 'non-prod', 'dr']
const clusterLabel: Record<string, string> = {
  'prod': 'Production',
  'non-prod': 'Non-Production',
  'dr': 'DR',
}

const barColors = ['bg-blue-500', 'bg-emerald-500', 'bg-violet-500', 'bg-orange-400']

export default function LicenseMonitoring() {
  const [clusterData, setClusterData] = useState<ClusterData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [activeCluster, setActiveCluster] = useState('prod')
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      setError('')
      const [snapshotsRes, capacityRes] = await Promise.all([
        licenseAPI.getSnapshots(),
        licenseAPI.getCapacity(),
      ])

      const snapshots: Snapshot[] = snapshotsRes.data
      const capacities: Capacity[] = capacityRes.data

      // Group snapshots by cluster
      const grouped: ClusterData[] = clusterKeys.map(clusterKey => {
        const clusterSnapshots = snapshots.filter(s => s.cluster === clusterKey)
        const capacity = capacities.find(c => c.environment === clusterKey)
        const total_vpcs = clusterSnapshots.reduce((sum, s) => sum + s.converted_quantity, 0)
        const last_updated = clusterSnapshots.length > 0
          ? clusterSnapshots[clusterSnapshots.length - 1].collected_at
          : ''

        return {
          cluster: clusterKey,
          total_vpcs,
          limit_vpcs: capacity?.total_licensed_vpc ?? 0,
          last_updated,
          products: clusterSnapshots.map(s => ({
            product_name: s.product_name,
            converted_quantity: s.converted_quantity,
          })),
        }
      })

      setClusterData(grouped)
    } catch (err) {
      setError('Failed to load license data.')
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    await fetchData()
    setRefreshing(false)
  }

  const cluster = clusterData.find(c => c.cluster === activeCluster)
  const pct = cluster && cluster.limit_vpcs > 0
    ? Math.round((cluster.total_vpcs / cluster.limit_vpcs) * 100)
    : 0
  const barColor = pct >= 80 ? 'bg-red-500' : pct >= 60 ? 'bg-amber-400' : 'bg-blue-500'
  const maxVpc = cluster && cluster.products.length > 0
    ? Math.max(...cluster.products.map(p => p.converted_quantity))
    : 1

  return (
    <div className="space-y-4">

      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="text-sm font-bold text-slate-800">License Monitoring</div>
        <div className="ml-auto flex gap-2">
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

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-600 font-semibold">
          {error}
          <button onClick={fetchData} className="ml-3 underline">Retry</button>
        </div>
      )}

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

      {!loading && !error && cluster && (
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
                  <div className="text-sm font-bold text-slate-800 mt-1">
                    {cluster.last_updated ? new Date(cluster.last_updated).toLocaleString() : '—'}
                  </div>
                </div>
                <div>
                  <div className="text-xs font-bold text-slate-400 uppercase tracking-wide">Products Running</div>
                  <div className="text-sm font-bold text-slate-800 mt-1">{cluster.products.length}</div>
                </div>
                <div>
                  <div className="text-xs font-bold text-slate-400 uppercase tracking-wide">Limit</div>
                  <div className="text-sm font-bold text-slate-800 mt-1">{cluster.limit_vpcs} VPCs</div>
                </div>
              </div>
              <div className="mt-4">
                <div className="w-full bg-slate-100 rounded-full h-2.5">
                  <div className={`h-2.5 rounded-full ${barColor}`} style={{ width: `${Math.min(pct, 100)}%` }} />
                </div>
                <div className="text-xs text-slate-400 mt-1">{pct}% of {cluster.limit_vpcs} VPC limit</div>
              </div>
            </div>

            {/* Product Breakdown Table */}
            <div className="bg-white rounded-xl border border-slate-200 p-5">
              <div className="text-sm font-bold text-slate-800 mb-4">Product Breakdown</div>
              {cluster.products.length === 0 ? (
                <div className="text-xs text-slate-400 text-center py-6">No data for this cluster.</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="border-b border-slate-100">
                        {['Product', 'VPCs Used', '% of Total'].map(h => (
                          <th key={h} className="text-left py-2 px-3 text-slate-400 font-bold uppercase tracking-wide">{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {cluster.products.map(p => (
                        <tr key={p.product_name} className="border-b border-slate-50 hover:bg-slate-50">
                          <td className="py-2 px-3 font-semibold text-slate-800">{p.product_name}</td>
                          <td className="py-2 px-3 font-bold text-blue-600">{p.converted_quantity}</td>
                          <td className="py-2 px-3 text-slate-500">
                            {cluster.total_vpcs > 0
                              ? `${Math.round((p.converted_quantity / cluster.total_vpcs) * 100)}%`
                              : '—'}
                          </td>
                        </tr>
                      ))}
                      <tr className="bg-slate-50 font-bold">
                        <td className="py-2 px-3 text-slate-800">Total</td>
                        <td className="py-2 px-3 text-slate-800">{cluster.total_vpcs}</td>
                        <td className="py-2 px-3 text-slate-800">100%</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>

          {/* Right */}
          <div className="space-y-4">

            {/* Bar Chart */}
            <div className="bg-white rounded-xl border border-slate-200 p-5">
              <div className="text-sm font-bold text-slate-800 mb-4">
                VPC Usage by Product — {clusterLabel[activeCluster]}
              </div>
              {cluster.products.length === 0 ? (
                <div className="text-xs text-slate-400 text-center py-6">No data for this cluster.</div>
              ) : (
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
              )}
            </div>

            {/* Cluster Summary */}
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-5">
              <div className="text-xs font-bold text-blue-700 mb-3">📊 Cluster Summary</div>
              <div className="space-y-2 text-xs">
                {[
                  ['Cluster', clusterLabel[activeCluster]],
                  ['Total VPCs Used', String(cluster.total_vpcs)],
                  ['Available', String(cluster.limit_vpcs - cluster.total_vpcs)],
                  ['Utilization', `${pct}%`],
                  ['Products Running', String(cluster.products.length)],
                ].map(([label, value]) => (
                  <div key={label} className="flex justify-between">
                    <span className="text-slate-500">{label}</span>
                    <span className={`font-bold ${
                      label === 'Utilization'
                        ? pct >= 80 ? 'text-red-600' : pct >= 60 ? 'text-amber-600' : 'text-green-600'
                        : label === 'Total VPCs Used' ? 'text-blue-600'
                        : label === 'Available' ? 'text-green-600'
                        : 'text-slate-800'
                    }`}>{value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {!loading && !error && cluster && cluster.products.length === 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-12 text-center text-slate-400 text-sm font-semibold">
          No license data available for {clusterLabel[activeCluster]}.
        </div>
      )}
    </div>
  )
}