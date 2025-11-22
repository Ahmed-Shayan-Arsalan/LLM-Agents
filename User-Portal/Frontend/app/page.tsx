'use client'

import { useEffect, useState } from 'react'
import ChatInterface from '@/components/ChatInterface'
import { Agent } from '@/types/agent'
import { getAgents } from '@/services/api'
import toast from 'react-hot-toast'

export default function Home() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)
  const [showDropdown, setShowDropdown] = useState(false)
  const [chatAnimating, setChatAnimating] = useState(false)

  useEffect(() => {
    fetchAgents()
  }, [])

  const fetchAgents = async () => {
    try {
      setLoading(true)
      const data = await getAgents()
      setAgents(data)
      // Show dropdown after agents are loaded
      if (data.length > 0) {
        setTimeout(() => setShowDropdown(true), 300)
      }
    } catch (error) {
      toast.error('Failed to fetch agents')
      console.error('Error fetching agents:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSelectAgent = (agent: Agent) => {
    setChatAnimating(true)
    setTimeout(() => {
      setSelectedAgent(agent)
      setShowDropdown(false)
      setChatAnimating(false)
    }, 200)
  }

  const handleBackToSelection = () => {
    setChatAnimating(true)
    setTimeout(() => {
      setSelectedAgent(null)
      setShowDropdown(true)
      setChatAnimating(false)
    }, 200)
  }

  if (selectedAgent) {
    return (
      <div className={`h-screen overflow-hidden ${chatAnimating ? 'opacity-0 scale-95 transition-all duration-200' : 'opacity-100 scale-100 transition-all duration-200'}`}>
        <ChatInterface
          agent={selectedAgent}
          agents={agents}
          onBack={handleBackToSelection}
          onSwitchAgent={handleSelectAgent}
        />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#343541] text-gray-100 flex items-center justify-center">
      <div className={`text-center transition-all duration-500 ${showDropdown ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
        <div className="mb-8">
          <div className="text-7xl mb-4 animate-bounce">🤖</div>
          <h1 className="text-5xl font-bold text-white mb-4">Choose Your AI Agent</h1>
          <p className="text-xl text-gray-400">Select an agent to start chatting</p>
        </div>

        {loading ? (
          <div className="flex justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#10a37f]"></div>
          </div>
        ) : agents.length === 0 ? (
          <div className="text-gray-400">No agents available</div>
        ) : (
          <div className="relative inline-block">
            <select
              onChange={(e) => {
                const agent = agents.find(a => a.name === e.target.value)
                if (agent) handleSelectAgent(agent)
              }}
              className="appearance-none bg-[#40414f] border-2 border-[#10a37f] rounded-lg px-8 py-4 text-white text-lg font-semibold cursor-pointer hover:bg-[#4a4b5a] transition-all focus:outline-none focus:ring-2 focus:ring-[#10a37f] min-w-[300px]"
              defaultValue=""
            >
              <option value="" disabled>Select an agent...</option>
              {agents.map((agent) => (
                <option key={agent._id} value={agent.name} className="bg-[#40414f]">
                  {agent.name}
                </option>
              ))}
            </select>
            <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none">
              <svg className="w-6 h-6 text-[#10a37f]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
