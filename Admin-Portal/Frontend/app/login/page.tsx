'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { login, verifyAuth } from '@/services/api'
import toast from 'react-hot-toast'

export default function LoginPage() {
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [checking, setChecking] = useState(true)
  const router = useRouter()

  useEffect(() => {
    // Check if already authenticated
    const checkAuth = async () => {
      const token = localStorage.getItem('admin_token')
      if (token) {
        const isAuthenticated = await verifyAuth()
        if (isAuthenticated) {
          router.push('/')
          return
        }
      }
      setChecking(false)
    }
    checkAuth()
  }, [router])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!password.trim()) {
      toast.error('Please enter a password')
      return
    }

    setLoading(true)
    try {
      const result = await login(password)
      if (result.success && result.token) {
        localStorage.setItem('admin_token', result.token)
        toast.success('Login successful!')
        router.push('/')
      } else {
        toast.error('Invalid password')
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  if (checking) {
    return (
      <div className="min-h-screen bg-[#343541] flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#10a37f]"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#343541] flex items-center justify-center">
      <div className="w-full max-w-md">
        <div className="bg-[#40414f] rounded-lg shadow-xl p-8 border border-gray-700/50">
          <div className="text-center mb-8">
            <div className="text-6xl mb-4">🔐</div>
            <h1 className="text-3xl font-bold text-white mb-2">Admin Portal</h1>
            <p className="text-gray-400">Enter password to continue</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-2">
                Password
              </label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
                className="w-full px-4 py-3 bg-[#343541] border border-gray-600/50 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#10a37f] focus:border-transparent disabled:opacity-50"
                placeholder="Enter admin password"
                autoFocus
              />
            </div>

            <button
              type="submit"
              disabled={loading || !password.trim()}
              className="w-full px-6 py-3 bg-[#10a37f] hover:bg-[#0d8f6e] text-white rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-[#10a37f]/20"
            >
              {loading ? 'Logging in...' : 'Login'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

