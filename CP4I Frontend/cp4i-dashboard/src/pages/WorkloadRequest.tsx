import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { workloadAPI } from '../services/api'

const products = [
  { value: 'ACE', label: 'ACE — App Connect Enterprise', ratio: '1:3', mult: 3 },
  { value: 'MQ', label: 'MQ — MQ Advanced', ratio: '2:1', mult: 0.5 },
  { value: 'APIC', label: 'APIC — API Connect', ratio: '1:1', mult: 1 },
  { value: 'DataPower', label: 'DataPower — Gateway', ratio: '1:1', mult: 1 },
]

const clusters = [
  { value: 'prod', label: 'Production', currentVpcs: 37 },
  { value: 'non-prod', label: 'Non-Production', currentVpcs: 13 },
  { value: 'dr', label: 'DR', currentVpcs: 25 },
]

export default function WorkloadRequest() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    workloadName: '',
    product: '',
    cluster: '',
    cpu: '',
    goLiveDate: '',
    justification: '',
  })
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const selectedProduct = products.find(p => p.value === form.product)
  const selectedCluster = clusters.find(c => c.value === form.cluster)
  const cpu = parseFloat(form.cpu) || 0
  const estimatedVpc = selectedProduct && cpu > 0
    ? Math.ceil((cpu / 2) * selectedProduct.mult)
    : null

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }))
  }

  const handleSubmit = async () => {
    if (!form.workloadName || !form.product || !form.cluster || !form.cpu || !form.goLiveDate || !form.justification) {
      setError('Please fill all required fields.')
      return
    }

    setSubmitting(true)
    setError('')

    try {
      const user = JSON.parse(localStorage.getItem('cp4i_user') || '{}')

      // POST /workload-requests now handles assessment + approval automatically
      const response = await workloadAPI.submit({
        workload_name: form.workloadName,
        product_type: form.product,
        estimated_cpu: parseFloat(form.cpu),
        business_justification: form.justification,
        requested_by: user.username,
        go_live_date: form.goLiveDate,
        cluster: form.cluster,
      })

      // Grab assessment_id from response and navigate to detail page
      const assessmentId = response.data.assessment_id
      navigate(`/assessments/${assessmentId}`)

    } catch (err: any) {
      setError(err.response?.data?.detail || 'Submission failed. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="grid grid-cols-2 gap-6 items-start">

      {/* Left — Form */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <div className="text-sm font-bold text-slate-800 mb-1">New Workload Request</div>
        <div className="text-xs text-slate-400 mb-6">Fill in the details below. VPC estimate updates live as you type.</div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-xs text-red-600 font-semibold mb-4">
            {error}
          </div>
        )}

        <div className="mb-4">
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            Workload Name <span className="text-red-500">*</span>
          </label>
          <input
            name="workloadName"
            value={form.workloadName}
            onChange={handleChange}
            className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            placeholder="e.g. Customer Onboarding API"
          />
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Product Type <span className="text-red-500">*</span>
            </label>
            <select
              name="product"
              value={form.product}
              onChange={handleChange}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            >
              <option value="">Select product</option>
              {products.map(p => (
                <option key={p.value} value={p.value}>{p.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Target Cluster <span className="text-red-500">*</span>
            </label>
            <select
              name="cluster"
              value={form.cluster}
              onChange={handleChange}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            >
              <option value="">Select cluster</option>
              {clusters.map(c => (
                <option key={c.value} value={c.value}>{c.label} ({c.currentVpcs} VPCs used)</option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Estimated CPU <span className="text-red-500">*</span>
            </label>
            <input
              name="cpu"
              value={form.cpu}
              onChange={handleChange}
              type="number"
              min="0.5"
              step="0.5"
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              placeholder="e.g. 2"
            />
            <div className="text-xs text-slate-400 mt-1">Number of CPUs this workload needs</div>
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Go Live Date <span className="text-red-500">*</span>
            </label>
            <input
              name="goLiveDate"
              value={form.goLiveDate}
              onChange={handleChange}
              type="date"
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            />
          </div>
        </div>

        <div className="mb-6">
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            Business Justification <span className="text-red-500">*</span>
          </label>
          <textarea
            name="justification"
            value={form.justification}
            onChange={handleChange}
            rows={3}
            className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 resize-none"
            placeholder="Explain why this workload is needed..."
          />
        </div>

        <div className="flex gap-2">
          <button
            onClick={handleSubmit}
            disabled={submitting}
            className="px-4 py-2 bg-blue-600 text-white text-xs font-bold rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submitting ? 'Submitting...' : 'Submit Request'}
          </button>
          <button className="px-4 py-2 border border-slate-200 text-slate-600 text-xs font-bold rounded-lg hover:bg-slate-50 transition-colors">
            Save as Draft
          </button>
          <button className="px-4 py-2 text-slate-400 text-xs font-bold rounded-lg hover:bg-slate-50 transition-colors ml-auto">
            Cancel
          </button>
        </div>
      </div>

      {/* Right — Live Preview Panel */}
      <div className="space-y-4">
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-5">
          <div className="text-xs font-bold text-blue-700 mb-4">📊 Live Capacity Preview</div>
          <div className="space-y-3">
            <div className="flex justify-between items-center py-2 border-b border-blue-100">
              <span className="text-xs text-slate-500">Selected Cluster Usage</span>
              <span className="text-sm font-bold text-slate-800">
                {selectedCluster ? `${selectedCluster.currentVpcs} VPCs (${selectedCluster.label})` : '—'}
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-blue-100">
              <span className="text-xs text-slate-500">Product Ratio</span>
              <span className="text-sm font-bold text-slate-800">
                {selectedProduct ? selectedProduct.ratio : '—'}
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-blue-100">
              <span className="text-xs text-slate-500">Formula</span>
              <span className="text-sm font-bold text-slate-800">
                {selectedProduct && cpu > 0
                  ? `CEILING(${cpu / 2} × ${selectedProduct.mult})`
                  : '—'}
              </span>
            </div>
          </div>
          <div className="bg-slate-800 rounded-xl p-4 mt-4 text-center">
            <div className="text-xs text-slate-400 uppercase tracking-wider">Estimated VPCs Required</div>
            <div className="text-4xl font-extrabold text-white mt-2">
              {estimatedVpc !== null ? estimatedVpc : '—'}
            </div>
            {estimatedVpc !== null && selectedCluster && (
              <div className="text-xs text-slate-400 mt-2">
                Projected total: {selectedCluster.currentVpcs + estimatedVpc} VPCs on {selectedCluster.label}
              </div>
            )}
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="text-xs font-bold text-slate-700 mb-3">IBM Ratio Reference</div>
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-slate-100">
                <th className="text-left py-1.5 text-slate-400 font-bold uppercase">Product</th>
                <th className="text-left py-1.5 text-slate-400 font-bold uppercase">Env</th>
                <th className="text-left py-1.5 text-slate-400 font-bold uppercase">Ratio</th>
              </tr>
            </thead>
            <tbody>
              {[
                ['ACE', 'Prod', '1:3'],
                ['ACE', 'Non-Prod', '2:3'],
                ['MQ Advanced', 'Prod', '2:1'],
                ['MQ Advanced', 'Non-Prod', '4:1'],
                ['APIC', 'Prod', '1:1'],
                ['DataPower', 'Prod', '1:1'],
              ].map(([product, env, ratio]) => (
                <tr key={`${product}-${env}`} className="border-b border-slate-50">
                  <td className="py-1.5 text-slate-700">{product}</td>
                  <td className="py-1.5 text-slate-500">{env}</td>
                  <td className="py-1.5 font-bold text-blue-600">{ratio}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}