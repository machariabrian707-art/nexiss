import { useState } from 'react'
import { Server, RefreshCw } from 'lucide-react'

const MOCK_LOGS = [
  { time: '10:42:01', level: 'INFO',  msg: 'Document abc123 — OCR complete, 4 pages' },
  { time: '10:42:03', level: 'INFO',  msg: 'Document abc123 — LLM extraction complete' },
  { time: '10:41:58', level: 'WARN',  msg: 'Document xyz789 — low OCR confidence (0.61)' },
  { time: '10:41:45', level: 'ERROR', msg: 'Document qwe456 — S3 upload timeout, retry 1/3' },
  { time: '10:41:30', level: 'INFO',  msg: 'Worker nexiss-worker-2 started' },
  { time: '10:40:11', level: 'INFO',  msg: 'Automation trigger: invoice_received → notify_finance' },
  { time: '10:39:55', level: 'INFO',  msg: 'Entity matched: "Doshi Holdings" → org_entity_id:e_88' },
]

const levelColor: Record<string, string> = {
  INFO:  'text-green-400',
  WARN:  'text-yellow-400',
  ERROR: 'text-red-400',
}

export default function AdminSystemPage() {
  const [filter, setFilter] = useState('ALL')

  const logs = filter === 'ALL' ? MOCK_LOGS : MOCK_LOGS.filter((l) => l.level === filter)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Server size={22} className="text-brand-500" />
          <h1 className="text-2xl font-bold text-gray-900">System Logs</h1>
        </div>
        <button className="btn-secondary text-sm flex items-center gap-1">
          <RefreshCw size={13} /> Refresh
        </button>
      </div>

      {/* Filter */}
      <div className="flex gap-2">
        {['ALL', 'INFO', 'WARN', 'ERROR'].map((l) => (
          <button
            key={l}
            onClick={() => setFilter(l)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
              filter === l ? 'bg-gray-900 text-white' : 'bg-white text-gray-600 ring-1 ring-gray-300 hover:bg-gray-50'
            }`}
          >
            {l}
          </button>
        ))}
      </div>

      {/* Log terminal */}
      <div className="bg-gray-900 rounded-2xl p-5 font-mono text-xs space-y-1.5 max-h-[60vh] overflow-y-auto">
        {logs.map((log, i) => (
          <div key={i} className="flex gap-3">
            <span className="text-gray-500 shrink-0">{log.time}</span>
            <span className={`shrink-0 font-bold ${levelColor[log.level]}`}>{log.level}</span>
            <span className="text-gray-300">{log.msg}</span>
          </div>
        ))}
        {logs.length === 0 && (
          <p className="text-gray-600">No logs match the current filter.</p>
        )}
      </div>

      {/* Worker status */}
      <div className="card p-6">
        <h2 className="font-semibold text-gray-800 mb-4">Workers</h2>
        <div className="grid grid-cols-3 gap-4">
          {['nexiss-worker-1', 'nexiss-worker-2', 'nexiss-worker-3'].map((w) => (
            <div key={w} className="flex items-center gap-3 bg-gray-50 p-3 rounded-lg">
              <span className="w-2 h-2 rounded-full bg-green-400" />
              <span className="text-sm text-gray-700">{w}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
