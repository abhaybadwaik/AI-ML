import { useState } from 'react'

interface Props {
  assessment: {
    workloadName: string
    product: string
    cluster: string
    estimatedCpu: number
    requiredVpc: number
    currentUsage: number
    projectedUsage: number
    availableHeadroom: number
    recommendation: string
    risk: string
  }
}

export default function AIAssessmentSummary({ assessment }: Props) {
  const [summary, setSummary] = useState('')
  const [loading, setLoading] = useState(false)
  const [generated, setGenerated] = useState(false)

  const generateSummary = async () => {
    setLoading(true)
    setSummary('')

    const prompt = `You are a CP4I License Assessment Analyst for Standard Bank Mozambique. 
    
Analyze this workload assessment and write a concise professional summary (3-4 sentences) for the approver to read before making a decision. 
Be specific with numbers. End with a clear recommendation statement.

Assessment Details:
- Workload Name: ${assessment.workloadName}
- Product: ${assessment.product}
- Target Cluster: ${assessment.cluster}
- Estimated CPU: ${assessment.estimatedCpu}
- Required VPCs: ${assessment.requiredVpc}
- Current Cluster Usage: ${assessment.currentUsage} VPCs
- Projected Usage After Approval: ${assessment.projectedUsage} VPCs
- Available Headroom After: ${assessment.availableHeadroom} VPCs
- Risk Level: ${assessment.risk}
- Engine Recommendation: ${assessment.recommendation}

Write only the summary paragraph. No headers, no bullet points, no extra formatting.`

    try {
      const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: 'claude-sonnet-4-20250514',
          max_tokens: 1000,
          messages: [
            { role: 'user', content: prompt }
          ],
        }),
      })

      const data = await response.json()
      const text = data.content?.[0]?.text || 'Unable to generate summary.'
      setSummary(text)
      setGenerated(true)
    } catch (err) {
      setSummary('Failed to generate AI summary. Please try again.')
      setGenerated(true)
    }

    setLoading(false)
  }

  return (
    <div className="bg-violet-50 border border-violet-200 rounded-xl p-5">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-lg">🤖</span>
          <div className="text-sm font-bold text-violet-800">AI Assessment Summary</div>
          <span className="bg-violet-100 text-violet-600 text-xs font-bold px-2 py-0.5 rounded-full">
            Powered by Claude
          </span>
        </div>
        {!generated && (
          <button
            onClick={generateSummary}
            disabled={loading}
            className="px-4 py-2 bg-violet-600 text-white text-xs font-bold rounded-lg hover:bg-violet-700 transition-colors disabled:opacity-50"
          >
            {loading ? 'Generating...' : '✨ Generate Summary'}
          </button>
        )}
        {generated && (
          <button
            onClick={() => { setGenerated(false); setSummary(''); generateSummary() }}
            disabled={loading}
            className="px-3 py-1.5 border border-violet-300 text-violet-600 text-xs font-semibold rounded-lg hover:bg-violet-100 transition-colors"
          >
            ↺ Regenerate
          </button>
        )}
      </div>

      {!generated && !loading && (
        <div className="text-xs text-violet-500 italic">
          Click Generate to get an AI-powered analysis of this assessment for the approver.
        </div>
      )}

      {loading && (
        <div className="flex items-center gap-3 py-2">
          <div className="flex gap-1">
            <div className="w-2 h-2 bg-violet-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <div className="w-2 h-2 bg-violet-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <div className="w-2 h-2 bg-violet-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
          <span className="text-xs text-violet-500">Claude is analyzing the assessment...</span>
        </div>
      )}

      {generated && summary && (
        <div className="text-sm text-violet-900 leading-relaxed">
          {summary}
        </div>
      )}
    </div>
  )
}