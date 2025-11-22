'use client'

import { useEffect, useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import Sidebar from '@/components/Sidebar'
import AgentDetails from '@/components/AgentDetails'
import { Agent } from '@/types/agent'
import { getAgents, deleteAgent, verifyAuth } from '@/services/api'
import toast from 'react-hot-toast'

export default function Home() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)
  const [isCreating, setIsCreating] = useState(false)
  const [checkingAuth, setCheckingAuth] = useState(true)
  const router = useRouter()

  const fetchAgents = useCallback(async () => {
    try {
      setLoading(true)
      const data = await getAgents()
      setAgents(data)
      // Auto-select first agent if none selected and not creating
      if (!selectedAgent && !isCreating && data.length > 0) {
        setSelectedAgent(data[0])
      }
    } catch (error) {
      toast.error('Failed to fetch agents')
      console.error('Error fetching agents:', error)
    } finally {
      setLoading(false)
    }
  }, [selectedAgent, isCreating])

  useEffect(() => {
    // Check authentication first
    const checkAuth = async () => {
      const token = localStorage.getItem('admin_token')
      if (!token) {
        router.push('/login')
        return
      }
      
      const isAuthenticated = await verifyAuth()
      if (!isAuthenticated) {
        localStorage.removeItem('admin_token')
        router.push('/login')
        return
      }
      
      setCheckingAuth(false)
      fetchAgents()
    }
    checkAuth()
  }, [router, fetchAgents])

  const handleSelectAgent = (agent: Agent) => {
    setSelectedAgent(agent)
    setIsCreating(false)
  }

  const handleAddNew = () => {
    setSelectedAgent(null)
    setIsCreating(true)
  }

  // Edit is now handled internally by AgentDetails component

  const handleDelete = async (agentId: string) => {
    if (!confirm('Are you sure you want to delete this agent?')) {
      return
    }

    try {
      await deleteAgent(agentId)
      toast.success('Agent deleted successfully')
      
      // If deleted agent was selected, select another or clear
      if (selectedAgent?._id === agentId) {
        const remainingAgents = agents.filter(a => a._id !== agentId)
        setSelectedAgent(remainingAgents[0] || null)
      }
      
      fetchAgents()
    } catch (error) {
      toast.error('Failed to delete agent')
      console.error('Error deleting agent:', error)
    }
  }

  const handleFormSuccess = () => {
    setIsCreating(false)
    fetchAgents().then(() => {
      // After fetching, select the newly created/updated agent
      if (selectedAgent?._id) {
        // Find the updated agent
        const updatedAgent = agents.find(a => a._id === selectedAgent._id)
        if (updatedAgent) {
          setSelectedAgent(updatedAgent)
        }
      }
    })
  }

  const handleFormClose = () => {
    if (isCreating) {
      setIsCreating(false)
      setSelectedAgent(agents[0] || null)
    }
  }

  if (checkingAuth) {
    return (
      <div className="min-h-screen bg-[#343541] flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#10a37f]"></div>
      </div>
    )
  }

  return (
    <div className="flex h-screen bg-[#343541] text-gray-100 overflow-hidden">
      {/* Left Sidebar */}
      <Sidebar
        agents={agents}
        loading={loading}
        selectedAgent={selectedAgent}
        onSelectAgent={handleSelectAgent}
        onAddNew={handleAddNew}
        onDelete={handleDelete}
      />

      {/* Right Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {isCreating || selectedAgent ? (
          <AgentDetails
            agent={selectedAgent}
            isCreating={isCreating}
            onClose={handleFormClose}
            onSuccess={handleFormSuccess}
          />
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <div className="text-6xl mb-4">🤖</div>
              <h2 className="text-2xl font-semibold text-gray-300 mb-2">
                No agent selected
              </h2>
              <p className="text-gray-400 mb-6">
                Select an agent from the sidebar or create a new one
              </p>
              <button
                onClick={handleAddNew}
                className="px-6 py-3 bg-[#10a37f] hover:bg-[#0d8f6e] text-white rounded-lg font-medium transition-colors shadow-lg shadow-[#10a37f]/20"
              >
                + Create New Agent
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
