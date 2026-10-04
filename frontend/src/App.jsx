import { useState, useEffect } from 'react'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function App() {
  // Global & Health state
  const [health, setHealth] = useState(null)
  const [apiError, setApiError] = useState(null)
  const [notification, setNotification] = useState(null)

  // Auth state
  const [token, setToken] = useState(() => localStorage.getItem('bt_token'))
  const [currentUser, setCurrentUser] = useState(null)
  const [authMode, setAuthMode] = useState('login') // 'login' | 'register'
  const [authLoading, setAuthLoading] = useState(false)
  const [authForm, setAuthForm] = useState({
    name: '',
    email: '',
    password: '',
    role: 'MEMBER',
  })

  // Navigation tab
  const [activeTab, setActiveTab] = useState(() => {
    if (typeof window !== 'undefined') {
      if (window.location.pathname === '/manager') return 'manager'
      if (window.location.pathname === '/dashboard') return 'member'
    }
    return 'member'
  })
  const [demoLoading, setDemoLoading] = useState(null) // 'MEMBER' | 'MANAGER' | null

  // Member state
  const [chatInput, setChatInput] = useState('')
  const [aiSubmitting, setAiSubmitting] = useState(false)
  const [lastExtractedItems, setLastExtractedItems] = useState(null)
  const [myRequests, setMyRequests] = useState([])
  const [editingItem, setEditingItem] = useState(null) // item object or null
  const [editForm, setEditForm] = useState({ quantity: 1, variant: '' })

  // Manager state
  const [managerTab, setManagerTab] = useState('combined') // 'combined' | 'breakdown'
  const [combinedData, setCombinedData] = useState(null)
  const [allMemberRequests, setAllMemberRequests] = useState([])
  const [pricingInputs, setPricingInputs] = useState({}) // { [itemId]: number }

  const showNotify = (msg, type = 'success') => {
    setNotification({ msg, type })
    setTimeout(() => setNotification(null), 4000)
  }

  // 1. Initial Health Check
  useEffect(() => {
    fetch(`${API_BASE}/api/v1/health`)
      .then((res) => {
        if (!res.ok) throw new Error(`Status ${res.status}`)
        return res.json()
      })
      .then((data) => {
        setHealth(data)
        setApiError(null)
      })
      .catch((err) => setApiError(err.message))
  }, [])

  // 2. Fetch User Profile if token exists & sync URL
  useEffect(() => {
    if (!token) {
      setCurrentUser(null)
      return
    }
    fetch(`${API_BASE}/api/v1/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => {
        if (!res.ok) throw new Error('Session expired')
        return res.json()
      })
      .then((user) => {
        setCurrentUser(user)
        const path = window.location.pathname
        if (path === '/manager' && user.role === 'MANAGER') {
          setActiveTab('manager')
        } else if (path === '/dashboard') {
          setActiveTab('member')
        } else if (user.role === 'MANAGER') {
          setActiveTab('manager')
          window.history.replaceState(null, '', '/manager')
        } else {
          setActiveTab('member')
          window.history.replaceState(null, '', '/dashboard')
        }
      })
      .catch(() => {
        setToken(null)
        localStorage.removeItem('bt_token')
      })
  }, [token])

  // Handle browser back/forward history navigation
  useEffect(() => {
    const handlePopState = () => {
      const path = window.location.pathname
      if (path === '/manager') setActiveTab('manager')
      else if (path === '/dashboard') setActiveTab('member')
    }
    window.addEventListener('popstate', handlePopState)
    return () => window.removeEventListener('popstate', handlePopState)
  }, [])

  // 3. Fetch Member Requests
  const fetchMyRequests = async () => {
    if (!token) return
    try {
      const res = await fetch(`${API_BASE}/api/v1/requests`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.ok) {
        const data = await res.json()
        setMyRequests(data)
      }
    } catch (e) {
      console.error('Failed to fetch requests', e)
    }
  }

  // 4. Fetch Manager Data
  const fetchManagerData = async () => {
    if (!token || currentUser?.role !== 'MANAGER') return
    try {
      const [resCombined, resAll] = await Promise.all([
        fetch(`${API_BASE}/api/v1/manager/combined`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch(`${API_BASE}/api/v1/manager/requests`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
      ])
      if (resCombined.ok) {
        const cData = await resCombined.json()
        setCombinedData(cData)
      }
      if (resAll.ok) {
        const aData = await resAll.json()
        setAllMemberRequests(aData)
      }
    } catch (e) {
      console.error('Failed to fetch manager data', e)
    }
  }

  useEffect(() => {
    if (currentUser) {
      fetchMyRequests()
      if (currentUser.role === 'MANAGER') {
        fetchManagerData()
      }
    }
  }, [currentUser])

  // Auth Handlers
  const handleAuthSubmit = async (e) => {
    e.preventDefault()
    setAuthLoading(true)
    try {
      if (authMode === 'register') {
        const regRes = await fetch(`${API_BASE}/api/v1/auth/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(authForm),
        })
        const regData = await regRes.json()
        if (!regRes.ok) throw new Error(regData.detail || 'Registration failed')
      }

      // Login
      const logRes = await fetch(`${API_BASE}/api/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: authForm.email, password: authForm.password }),
      })
      const logData = await logRes.json()
      if (!logRes.ok) throw new Error(logData.detail || 'Login failed')

      localStorage.setItem('bt_token', logData.access_token)
      setToken(logData.access_token)
      showNotify(`Welcome! Authenticated as ${authForm.email}`)
    } catch (err) {
      showNotify(err.message, 'error')
    } finally {
      setAuthLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('bt_token')
    setToken(null)
    setCurrentUser(null)
    setMyRequests([])
    setCombinedData(null)
    window.history.pushState(null, '', '/')
    showNotify('Logged out successfully.')
  }

  // Server-side 1-Click Demo Login (Zero client credentials)
  const handleDemoLogin = async (role) => {
    setDemoLoading(role)
    try {
      const res = await fetch(`${API_BASE}/api/v1/auth/demo-login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role }),
      })
      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.detail || 'Demo login failed')
      }

      localStorage.setItem('bt_token', data.access_token)
      setToken(data.access_token)
      setCurrentUser(data.user)
      if (role === 'MANAGER') {
        setActiveTab('manager')
        window.history.pushState(null, '', '/manager')
      } else {
        setActiveTab('member')
        window.history.pushState(null, '', '/dashboard')
      }
      showNotify(`Welcome! Authenticated as ${data.user.name}`)
    } catch (err) {
      showNotify(err.message, 'error')
    } finally {
      setDemoLoading(null)
    }
  }

  // AI Extraction & Request Submission
  const handleSendAiMessage = async (e) => {
    e?.preventDefault()
    if (!chatInput.trim()) return

    setAiSubmitting(true)
    try {
      const res = await fetch(`${API_BASE}/api/v1/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ text: chatInput.trim() }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Failed to process message')

      const itemsList = data.extracted_items || data.items || []
      setLastExtractedItems(itemsList)
      setChatInput('')
      showNotify(`AI successfully extracted ${itemsList.length} item(s)!`)
      fetchMyRequests()
      if (currentUser?.role === 'MANAGER') fetchManagerData()
    } catch (err) {
      showNotify(err.message, 'error')
    } finally {
      setAiSubmitting(false)
    }
  }

  // Delete Item
  const handleDeleteItem = async (itemId) => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/requests/${itemId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Failed to delete item')
      setMyRequests((prev) => prev.filter((it) => it.id !== itemId))
      showNotify('Item deleted successfully.')
      if (currentUser?.role === 'MANAGER') fetchManagerData()
    } catch (err) {
      showNotify(err.message, 'error')
    }
  }

  // Update Item
  const handleSaveEdit = async () => {
    if (!editingItem) return
    try {
      const res = await fetch(`${API_BASE}/api/v1/requests/${editingItem.id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          quantity: Number(editForm.quantity),
          variant: editForm.variant,
        }),
      })
      if (!res.ok) throw new Error('Failed to update item')
      const updated = await res.json()
      setMyRequests((prev) => prev.map((it) => (it.id === updated.id ? updated : it)))
      setEditingItem(null)
      showNotify('Item updated successfully.')
      if (currentUser?.role === 'MANAGER') fetchManagerData()
    } catch (err) {
      showNotify(err.message, 'error')
    }
  }

  // Manager: Update Unit Price
  const handleSetPrice = async (itemId) => {
    const p = pricingInputs[itemId]
    if (p === undefined || p === '') return
    try {
      const res = await fetch(`${API_BASE}/api/v1/manager/requests/${itemId}/price`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ unit_price: parseFloat(p) }),
      })
      if (!res.ok) throw new Error('Failed to update price')
      showNotify('Price assigned successfully.')
      fetchManagerData()
    } catch (err) {
      showNotify(err.message, 'error')
    }
  }

  // Manager: Update Status
  const handleUpdateStatus = async (itemId, newStatus) => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/manager/requests/${itemId}/status`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ status: newStatus }),
      })
      if (!res.ok) throw new Error('Failed to update status')
      showNotify(`Status changed to ${newStatus}`)
      fetchManagerData()
    } catch (err) {
      showNotify(err.message, 'error')
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Toast Notification */}
      {notification && (
        <div
          className={`fixed top-4 right-4 z-50 px-4 py-3 rounded-xl shadow-2xl border text-sm font-medium transition-all ${
            notification.type === 'error'
              ? 'bg-rose-950/90 border-rose-700 text-rose-200'
              : 'bg-emerald-950/90 border-emerald-700 text-emerald-200'
          }`}
        >
          {notification.msg}
        </div>
      )}

      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-md sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center text-xl font-bold shadow-lg shadow-indigo-500/20">
              🛒
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg text-white">Buy Together</span>
                <span className="text-xs bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 px-2 py-0.5 rounded-full font-mono">
                  MVP Live
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">
                AI-Powered Group Purchasing & Demand Aggregator
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            {/* Backend Status indicator */}
            <div className="hidden sm:flex items-center gap-2 bg-slate-800/80 border border-slate-700/60 px-3 py-1 rounded-full text-xs">
              <span
                className={`w-2 h-2 rounded-full ${
                  health ? 'bg-emerald-400 shadow-sm shadow-emerald-400/50' : 'bg-rose-500 animate-pulse'
                }`}
              />
              <span className="text-slate-300">
                {health ? `Backend: ${health.ai_provider} AI` : apiError ? 'Offline' : 'Connecting...'}
              </span>
            </div>

            {/* Auth status & actions */}
            {currentUser ? (
              <div className="flex items-center gap-3">
                <div className="text-right hidden sm:block">
                  <div className="text-xs font-semibold text-slate-200">{currentUser.name}</div>
                  <span
                    className={`text-[10px] px-1.5 py-0.5 rounded font-mono font-medium ${
                      currentUser.role === 'MANAGER'
                        ? 'bg-purple-900/60 text-purple-300 border border-purple-700'
                        : 'bg-blue-900/60 text-blue-300 border border-blue-700'
                    }`}
                  >
                    {currentUser.role}
                  </span>
                </div>
                <button
                  onClick={handleLogout}
                  className="text-xs bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 px-3 py-1.5 rounded-lg transition cursor-pointer"
                >
                  Logout
                </button>
              </div>
            ) : (
              <span className="text-xs text-slate-400">Not authenticated</span>
            )}
          </div>
        </div>

        {/* Tab Bar if authenticated */}
        {currentUser && (
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 border-t border-slate-800/80 flex space-x-2 py-2">
            <button
              onClick={() => {
                setActiveTab('member')
                window.history.pushState(null, '', '/dashboard')
              }}
              className={`px-4 py-1.5 rounded-lg text-xs font-medium transition cursor-pointer ${
                activeTab === 'member'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              Member Portal & Requests
            </button>
            {currentUser.role === 'MANAGER' && (
              <button
                onClick={() => {
                  setActiveTab('manager')
                  window.history.pushState(null, '', '/manager')
                }}
                className={`px-4 py-1.5 rounded-lg text-xs font-medium transition cursor-pointer ${
                  activeTab === 'manager'
                    ? 'bg-purple-600 text-white shadow-md shadow-purple-600/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`}
              >
                Manager Procurement Dashboard
              </button>
            )}
          </div>
        )}
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!currentUser ? (
          /* LOGIN / REGISTRATION VIEW */
          <div className="max-w-md mx-auto my-12 bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl space-y-6">
            <div className="text-center space-y-1">
              <h2 className="text-2xl font-bold text-white">
                {authMode === 'login' ? 'Sign In' : 'Create Account'}
              </h2>
              <p className="text-xs text-slate-400">
                Join the group to request items or manage procurement
              </p>
            </div>

            {/* Quick Demo Section */}
            <div className="bg-slate-950/80 border border-indigo-500/30 rounded-2xl p-5 shadow-xl space-y-3">
              <div className="text-center space-y-1">
                <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  ⚡ Quick Demo
                </div>
                <h3 className="text-base font-bold text-white tracking-tight">
                  Try Buy Together instantly:
                </h3>
                <p className="text-xs text-slate-400">
                  No account required for the demo.
                </p>
              </div>

              <div className="space-y-2.5 pt-1">
                <button
                  type="button"
                  id="btn-demo-member"
                  onClick={() => handleDemoLogin('MEMBER')}
                  disabled={demoLoading !== null || authLoading}
                  className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 active:scale-[0.99] transition shadow-lg shadow-indigo-600/25 border border-indigo-400/30 cursor-pointer disabled:opacity-50"
                >
                  {demoLoading === 'MEMBER' ? (
                    <span className="inline-flex items-center gap-2">
                      <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                      Authenticating Member...
                    </span>
                  ) : (
                    <>
                      <span className="text-base">🚀</span>
                      <span>Continue as Demo Member</span>
                    </>
                  )}
                </button>

                <button
                  type="button"
                  id="btn-demo-manager"
                  onClick={() => handleDemoLogin('MANAGER')}
                  disabled={demoLoading !== null || authLoading}
                  className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 active:scale-[0.99] transition shadow-lg shadow-purple-600/25 border border-purple-400/30 cursor-pointer disabled:opacity-50"
                >
                  {demoLoading === 'MANAGER' ? (
                    <span className="inline-flex items-center gap-2">
                      <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                      Authenticating Manager...
                    </span>
                  ) : (
                    <>
                      <span className="text-base">👑</span>
                      <span>Continue as Demo Manager</span>
                    </>
                  )}
                </button>
              </div>

              <div className="text-[11px] text-slate-500 text-center pt-1 border-t border-slate-800/80">
                Direct server-side authentication • Real session issued
              </div>
            </div>

            {/* Divider */}
            <div className="relative flex items-center justify-center my-1">
              <div className="border-t border-slate-800 w-full" />
              <span className="bg-slate-900 px-3 text-[11px] uppercase tracking-wider text-slate-500 font-semibold absolute">
                or use regular credentials
              </span>
            </div>

            <form onSubmit={handleAuthSubmit} className="space-y-4">
              {authMode === 'register' && (
                <>
                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1">Full Name</label>
                    <input
                      type="text"
                      required
                      value={authForm.name}
                      onChange={(e) => setAuthForm({ ...authForm, name: e.target.value })}
                      placeholder="e.g. Alice Sharma"
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1">Role</label>
                    <select
                      value={authForm.role}
                      onChange={(e) => setAuthForm({ ...authForm, role: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                    >
                      <option value="MEMBER">Member (Submit & Track Items)</option>
                      <option value="MANAGER">Manager (Procurement & Aggregation)</option>
                    </select>
                  </div>
                </>
              )}

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Email</label>
                <input
                  type="email"
                  required
                  value={authForm.email}
                  onChange={(e) => setAuthForm({ ...authForm, email: e.target.value })}
                  placeholder="name@example.com"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Password</label>
                <input
                  type="password"
                  required
                  value={authForm.password}
                  onChange={(e) => setAuthForm({ ...authForm, password: e.target.value })}
                  placeholder="Minimum 8 characters"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <button
                type="submit"
                disabled={authLoading}
                className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium py-2.5 rounded-xl transition shadow-lg shadow-indigo-600/20 text-sm cursor-pointer"
              >
                {authLoading
                  ? 'Processing...'
                  : authMode === 'login'
                  ? 'Sign In'
                  : 'Register Account & Login'}
              </button>
            </form>

            <div className="text-center text-xs text-slate-400">
              {authMode === 'login' ? (
                <span>
                  Don&apos;t have an account?{' '}
                  <button
                    onClick={() => setAuthMode('register')}
                    className="text-indigo-400 hover:underline font-medium cursor-pointer"
                  >
                    Register here
                  </button>
                </span>
              ) : (
                <span>
                  Already registered?{' '}
                  <button
                    onClick={() => setAuthMode('login')}
                    className="text-indigo-400 hover:underline font-medium cursor-pointer"
                  >
                    Sign in here
                  </button>
                </span>
              )}
            </div>
          </div>
        ) : activeTab === 'member' ? (
          /* MEMBER DASHBOARD */
          <div className="space-y-8">
            {/* Natural Language Request Box */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-bold text-white flex items-center gap-2">
                    ✨ Natural Language Purchase Request
                  </h2>
                  <p className="text-xs text-slate-400">
                    Type what you need in Hinglish or English — AI will extract items, quantities, and units.
                  </p>
                </div>
                <span className="text-[11px] bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-2.5 py-1 rounded-full font-mono">
                  Gemma 4 12B Pipeline
                </span>
              </div>

              {/* Sample Chips */}
              <div className="flex flex-wrap items-center gap-2 text-xs">
                <span className="text-slate-500">Try quick sample:</span>
                {[
                  'bhai 2 notebook aur ek blue pen',
                  '5 packets of milk and 2 breads',
                  '3 pack sticky notes and 1 black marker',
                ].map((sample, i) => (
                  <button
                    key={i}
                    onClick={() => setChatInput(sample)}
                    className="bg-slate-800 hover:bg-slate-700/80 border border-slate-700 text-slate-300 px-2.5 py-1 rounded-full transition cursor-pointer"
                  >
                    &ldquo;{sample}&rdquo;
                  </button>
                ))}
              </div>

              <form onSubmit={handleSendAiMessage} className="flex gap-2">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder="e.g. bhai 2 notebook aur ek blue pen"
                  className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
                <button
                  type="submit"
                  disabled={aiSubmitting || !chatInput.trim()}
                  className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium px-5 py-3 rounded-xl transition shadow-lg shadow-indigo-600/20 text-sm whitespace-nowrap cursor-pointer"
                >
                  {aiSubmitting ? 'AI Extracting...' : 'Extract & Add Items'}
                </button>
              </form>

              {/* Extraction Feedback */}
              {lastExtractedItems && (
                <div className="bg-indigo-950/40 border border-indigo-800/60 rounded-xl p-4 space-y-2">
                  <div className="text-xs font-semibold text-indigo-300 uppercase tracking-wider flex items-center gap-1.5">
                    <span>⚡ AI Extraction Result:</span>
                    <span className="text-slate-400 font-normal">
                      ({lastExtractedItems.length} items parsed & saved)
                    </span>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                    {lastExtractedItems.map((item, idx) => (
                      <div
                        key={idx}
                        className="bg-slate-900 border border-indigo-900/80 rounded-lg p-2.5 flex items-center justify-between text-xs"
                      >
                        <div>
                          <span className="font-semibold text-white capitalize">{item.name}</span>
                          {item.variant && (
                            <span className="text-indigo-400 ml-1.5">({item.variant})</span>
                          )}
                        </div>
                        <span className="bg-indigo-600/30 text-indigo-200 border border-indigo-500/30 px-2 py-0.5 rounded font-mono font-medium">
                          {item.quantity} {item.unit}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* My Request Items List */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-bold text-white">📋 My Active Requests</h3>
                  <p className="text-xs text-slate-400">
                    Track your requested items. You can edit quantities or cancel pending items.
                  </p>
                </div>
                <button
                  onClick={fetchMyRequests}
                  className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-lg transition cursor-pointer"
                >
                  Refresh
                </button>
              </div>

              {myRequests.length === 0 ? (
                <div className="text-center py-12 border border-dashed border-slate-800 rounded-xl">
                  <p className="text-sm text-slate-400">No requests submitted yet.</p>
                  <p className="text-xs text-slate-500 mt-1">
                    Use the natural language input box above to submit your first items!
                  </p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead className="bg-slate-950/60 text-slate-400 text-xs uppercase tracking-wider border-b border-slate-800">
                      <tr>
                        <th className="py-3 px-4">Item Name</th>
                        <th className="py-3 px-4">Variant</th>
                        <th className="py-3 px-4">Quantity</th>
                        <th className="py-3 px-4">Unit</th>
                        <th className="py-3 px-4">Est. Unit Price</th>
                        <th className="py-3 px-4">Status</th>
                        <th className="py-3 px-4 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {myRequests.map((it) => (
                        <tr key={it.id} className="hover:bg-slate-800/30 transition">
                          <td className="py-3 px-4 font-medium text-white capitalize">{it.name}</td>
                          <td className="py-3 px-4 text-slate-300">
                            {it.variant ? (
                              <span className="bg-slate-800 px-2 py-0.5 rounded text-xs">
                                {it.variant}
                              </span>
                            ) : (
                              <span className="text-slate-600">—</span>
                            )}
                          </td>
                          <td className="py-3 px-4 font-mono font-medium text-indigo-300">
                            {it.quantity}
                          </td>
                          <td className="py-3 px-4 text-slate-400">{it.unit}</td>
                          <td className="py-3 px-4 text-slate-400">
                            {it.unit_price ? `₹${parseFloat(it.unit_price).toFixed(2)}` : 'Pending'}
                          </td>
                          <td className="py-3 px-4">
                            <span
                              className={`text-[11px] px-2 py-0.5 rounded-full font-medium ${
                                it.status === 'APPROVED'
                                  ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                                  : it.status === 'PURCHASED'
                                  ? 'bg-sky-950 text-sky-300 border border-sky-800'
                                  : it.status === 'REJECTED'
                                  ? 'bg-rose-950 text-rose-300 border border-rose-800'
                                  : 'bg-amber-950 text-amber-300 border border-amber-800'
                              }`}
                            >
                              {it.status}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-right space-x-2">
                            <button
                              onClick={() => {
                                setEditingItem(it)
                                setEditForm({ quantity: it.quantity, variant: it.variant || '' })
                              }}
                              className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-2.5 py-1 rounded transition cursor-pointer"
                            >
                              Edit
                            </button>
                            <button
                              onClick={() => handleDeleteItem(it.id)}
                              className="text-xs bg-rose-950/60 hover:bg-rose-900/60 border border-rose-800/80 text-rose-300 px-2.5 py-1 rounded transition cursor-pointer"
                            >
                              Delete
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {/* Inline Edit Modal */}
            {editingItem && (
              <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-sm w-full space-y-4 shadow-2xl">
                  <h3 className="font-bold text-white text-base">
                    Edit Request: <span className="capitalize text-indigo-400">{editingItem.name}</span>
                  </h3>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-xs font-medium text-slate-300 mb-1">Quantity</label>
                      <input
                        type="number"
                        min="1"
                        value={editForm.quantity}
                        onChange={(e) => setEditForm({ ...editForm, quantity: e.target.value })}
                        className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-slate-300 mb-1">
                        Variant / Details (Optional)
                      </label>
                      <input
                        type="text"
                        value={editForm.variant}
                        onChange={(e) => setEditForm({ ...editForm, variant: e.target.value })}
                        placeholder="e.g. blue, 500g, ruled"
                        className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white"
                      />
                    </div>
                  </div>
                  <div className="flex justify-end gap-2 pt-2">
                    <button
                      onClick={() => setEditingItem(null)}
                      className="text-xs bg-slate-800 text-slate-300 px-3 py-2 rounded-xl cursor-pointer"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleSaveEdit}
                      className="text-xs bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-4 py-2 rounded-xl shadow-md shadow-indigo-600/20 cursor-pointer"
                    >
                      Save Changes
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          /* MANAGER DASHBOARD */
          <div className="space-y-8">
            {/* KPI Cards */}
            {combinedData?.financial_summary && (
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
                  <div className="text-xs text-slate-400 font-medium">Distinct Products</div>
                  <div className="text-2xl font-bold text-white mt-1">
                    {combinedData.financial_summary.total_items_count}
                  </div>
                  <div className="text-[11px] text-slate-500 mt-0.5">Aggregated unique items</div>
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
                  <div className="text-xs text-slate-400 font-medium">Total Quantity (Units)</div>
                  <div className="text-2xl font-bold text-indigo-400 mt-1">
                    {combinedData.financial_summary.total_units_count}
                  </div>
                  <div className="text-[11px] text-slate-500 mt-0.5">Across all member requests</div>
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
                  <div className="text-xs text-slate-400 font-medium">Estimated Grand Total</div>
                  <div className="text-2xl font-bold text-emerald-400 mt-1">
                    ₹{parseFloat(combinedData.financial_summary.grand_total_cost).toFixed(2)}
                  </div>
                  <div className="text-[11px] text-slate-500 mt-0.5">Calculated from assigned prices</div>
                </div>
              </div>
            )}

            {/* Manager View Switcher */}
            <div className="flex border-b border-slate-800 space-x-4">
              <button
                onClick={() => setManagerTab('combined')}
                className={`pb-2.5 text-sm font-semibold transition border-b-2 cursor-pointer ${
                  managerTab === 'combined'
                    ? 'border-purple-500 text-purple-400'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                📊 Consolidated Procurement Requirements
              </button>
              <button
                onClick={() => setManagerTab('breakdown')}
                className={`pb-2.5 text-sm font-semibold transition border-b-2 cursor-pointer ${
                  managerTab === 'breakdown'
                    ? 'border-purple-500 text-purple-400'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                👥 All Member Requests Breakdown ({allMemberRequests.length})
              </button>
            </div>

            {managerTab === 'combined' ? (
              /* Combined Aggregate View */
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-base font-bold text-white">Dynamic Requirements Aggregation</h3>
                    <p className="text-xs text-slate-400">
                      Items grouped by item name, variant, and unit with consolidated quantities.
                    </p>
                  </div>
                  <button
                    onClick={fetchManagerData}
                    className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-lg transition cursor-pointer"
                  >
                    Refresh
                  </button>
                </div>

                {!combinedData?.items || combinedData.items.length === 0 ? (
                  <div className="text-center py-12 border border-dashed border-slate-800 rounded-xl">
                    <p className="text-sm text-slate-400">No member requirements available yet.</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                      <thead className="bg-slate-950/60 text-slate-400 text-xs uppercase tracking-wider border-b border-slate-800">
                        <tr>
                          <th className="py-3 px-4">Item & Variant</th>
                          <th className="py-3 px-4">Consolidated Qty</th>
                          <th className="py-3 px-4">Unit</th>
                          <th className="py-3 px-4">Requesters</th>
                          <th className="py-3 px-4">Avg Unit Price</th>
                          <th className="py-3 px-4">Total Cost</th>
                          <th className="py-3 px-4">Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60">
                        {combinedData.items.map((row, idx) => (
                          <tr key={idx} className="hover:bg-slate-800/30 transition">
                            <td className="py-3 px-4 font-semibold text-white capitalize">
                              {row.name}
                              {row.variant && (
                                <span className="text-purple-400 ml-1.5 font-normal text-xs">
                                  ({row.variant})
                                </span>
                              )}
                            </td>
                            <td className="py-3 px-4 font-mono font-bold text-purple-300 text-base">
                              {row.total_quantity}
                            </td>
                            <td className="py-3 px-4 text-slate-400">{row.unit}</td>
                            <td className="py-3 px-4">
                              <div className="flex flex-wrap gap-1">
                                {row.member_names.map((mName, mIdx) => (
                                  <span
                                    key={mIdx}
                                    className="bg-slate-800 border border-slate-700 text-slate-300 text-[11px] px-2 py-0.5 rounded-full"
                                  >
                                    {mName}
                                  </span>
                                ))}
                              </div>
                            </td>
                            <td className="py-3 px-4 text-slate-300">
                              {row.unit_price ? `₹${parseFloat(row.unit_price).toFixed(2)}` : '—'}
                            </td>
                            <td className="py-3 px-4 font-medium text-emerald-400">
                              {row.total_cost ? `₹${parseFloat(row.total_cost).toFixed(2)}` : '—'}
                            </td>
                            <td className="py-3 px-4">
                              <span className="text-[11px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded">
                                {row.status}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            ) : (
              /* Breakdown View with Price Assignment & Status Control */
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-base font-bold text-white">All Member Submissions</h3>
                    <p className="text-xs text-slate-400">
                      Assign wholesale unit prices and approve or purchase requests.
                    </p>
                  </div>
                  <button
                    onClick={fetchManagerData}
                    className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-lg transition cursor-pointer"
                  >
                    Refresh
                  </button>
                </div>

                {allMemberRequests.length === 0 ? (
                  <div className="text-center py-12 border border-dashed border-slate-800 rounded-xl">
                    <p className="text-sm text-slate-400">No requests found.</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                      <thead className="bg-slate-950/60 text-slate-400 text-xs uppercase tracking-wider border-b border-slate-800">
                        <tr>
                          <th className="py-3 px-4">Requester</th>
                          <th className="py-3 px-4">Item</th>
                          <th className="py-3 px-4">Qty & Unit</th>
                          <th className="py-3 px-4">Assign Unit Price</th>
                          <th className="py-3 px-4">Total</th>
                          <th className="py-3 px-4">Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60">
                        {allMemberRequests.map((it) => (
                          <tr key={it.id} className="hover:bg-slate-800/30 transition">
                            <td className="py-3 px-4">
                              <div className="font-medium text-white">{it.user_name}</div>
                              <div className="text-[11px] text-slate-500">{it.user_email}</div>
                            </td>
                            <td className="py-3 px-4 font-semibold text-white capitalize">
                              {it.name}
                              {it.variant && (
                                <span className="text-purple-400 ml-1 text-xs">({it.variant})</span>
                              )}
                            </td>
                            <td className="py-3 px-4 font-mono text-purple-300">
                              {it.quantity} {it.unit}
                            </td>
                            <td className="py-3 px-4">
                              <div className="flex items-center gap-1.5">
                                <span className="text-slate-400 text-xs">₹</span>
                                <input
                                  type="number"
                                  step="0.01"
                                  placeholder={it.unit_price ? String(it.unit_price) : 'Price'}
                                  value={pricingInputs[it.id] ?? ''}
                                  onChange={(e) =>
                                    setPricingInputs({ ...pricingInputs, [it.id]: e.target.value })
                                  }
                                  className="w-20 bg-slate-950 border border-slate-800 rounded px-2 py-1 text-xs text-white"
                                />
                                <button
                                  onClick={() => handleSetPrice(it.id)}
                                  className="text-xs bg-purple-600 hover:bg-purple-500 text-white px-2 py-1 rounded transition cursor-pointer"
                                >
                                  Save
                                </button>
                              </div>
                            </td>
                            <td className="py-3 px-4 text-emerald-400 font-mono">
                              {it.total_price ? `₹${parseFloat(it.total_price).toFixed(2)}` : '—'}
                            </td>
                            <td className="py-3 px-4">
                              <select
                                value={it.status}
                                onChange={(e) => handleUpdateStatus(it.id, e.target.value)}
                                className="bg-slate-950 border border-slate-800 text-xs rounded px-2 py-1 text-white focus:outline-none focus:border-purple-500 cursor-pointer"
                              >
                                <option value="PENDING">PENDING</option>
                                <option value="APPROVED">APPROVED</option>
                                <option value="PURCHASED">PURCHASED</option>
                                <option value="REJECTED">REJECTED</option>
                              </select>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 bg-slate-950/80 py-4 text-center text-xs text-slate-500">
        Buy Together • AI Group Purchasing & Request Aggregator • Hackathon MVP
      </footer>
    </div>
  )
}
