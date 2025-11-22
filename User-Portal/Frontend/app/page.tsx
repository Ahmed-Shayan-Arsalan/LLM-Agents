'use client'

import { useEffect, useState } from 'react'
import AgentSelection from '@/components/AgentSelection'
import ChatInterface from '@/components/ChatInterface'
import { Agent } from '@/types/agent'
import { getAgents } from '@/services/api'
import toast from 'react-hot-toast'

export default function Home() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)

  useEffect(() => {
    fetchAgents()
  }, [])

  const fetchAgents = async () => {
    try {
      setLoading(true)
      const data = await getAgents()
      setAgents(data)
    } catch (error) {
      toast.error('Failed to fetch agents')
      console.error('Error fetching agents:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSelectAgent = (agent: Agent) => {
    setSelectedAgent(agent)
  }

  const handleBackToSelection = () => {
    setSelectedAgent(null)
  }

  if (selectedAgent) {
    return (
      <ChatInterface
        agent={selectedAgent}
        onBack={handleBackToSelection}
      />
    )
  }

  return (
    <AgentSelection
      agents={agents}
      loading={loading}
      onSelectAgent={handleSelectAgent}
    />
  )
}



