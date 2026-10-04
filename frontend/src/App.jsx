import { useState, useEffect } from 'react'

function App() {
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/health')
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`)
        return res.json()
      })
      .then((data) => {
        setHealth(data)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-6">
      <div className="max-w-xl w-full bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl space-y-6">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center text-xl font-bold shadow-lg shadow-indigo-500/20">
            🛒
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white">Buy Together</h1>
            <p className="text-sm text-slate-400">AI-Powered Group Purchasing & Request Aggregator</p>
          </div>
        </div>

        <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-5 space-y-3">
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-400">Backend API Status:</span>
            {loading ? (
              <span className="text-amber-400 flex items-center gap-1.5 font-medium">
                <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>
                Checking...
              </span>
            ) : error ? (
              <span className="text-rose-400 flex items-center gap-1.5 font-medium">
                <span className="w-2 h-2 rounded-full bg-rose-400"></span>
                Offline ({error})
              </span>
            ) : (
              <span className="text-emerald-400 flex items-center gap-1.5 font-medium">
                <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                Live ({health?.status?.toUpperCase()})
              </span>
            )}
          </div>

          {health && (
            <div className="pt-2 border-t border-slate-800/80 grid grid-cols-2 gap-2 text-xs text-slate-300">
              <div>
                <span className="text-slate-500">AI Provider:</span>{' '}
                <code className="text-indigo-400 font-mono">{health.ai_provider}</code>
              </div>
              <div>
                <span className="text-slate-500">Environment:</span>{' '}
                <code className="text-emerald-400 font-mono">{health.environment}</code>
              </div>
              <div>
                <span className="text-slate-500">Version:</span>{' '}
                <code className="text-slate-300 font-mono">{health.version}</code>
              </div>
              <div>
                <span className="text-slate-500">FastAPI:</span>{' '}
                <code className="text-sky-400 font-mono">Running</code>
              </div>
            </div>
          )}
        </div>

        <div className="text-xs text-slate-500 text-center">
          Phase 1 Foundation Initialized • React + Vite + Tailwind CSS + FastAPI
        </div>
      </div>
    </div>
  )
}

export default App
