'use client'

import { Agent } from '@/types/agent'

interface AgentSelectionProps {
  agents: Agent[]
  loading: boolean
  onSelectAgent: (agent: Agent) => void
}

export default function AgentSelection({ agents, loading, onSelectAgent }: AgentSelectionProps) {
  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#343541]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#10a37f]"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#343541] text-gray-100">
      <div className="max-w-6xl mx-auto px-8 py-12">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4">Choose Your AI Agent</h1>
          <p className="text-xl text-gray-400">
            Select an agent to start interacting with specialized AI assistants
          </p>
        </div>

        {agents.length === 0 ? (
          <div className="text-center py-20">
            <div className="text-6xl mb-4">🤖</div>
            <p className="text-gray-400 text-lg">No agents available at the moment</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {agents.map((agent) => (
              <button
                key={agent._id}
                onClick={() => onSelectAgent(agent)}
                className="bg-[#40414f] hover:bg-[#4a4b5a] border border-gray-600/50 rounded-lg p-6 text-left transition-all hover:border-[#10a37f]/50 hover:shadow-lg hover:shadow-[#10a37f]/10"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="w-12 h-12 bg-[#10a37f] rounded-lg flex items-center justify-center text-2xl">
                    🤖
                  </div>
                  <div className="w-2 h-2 rounded-full bg-[#10a37f]"></div>
                </div>
                <h2 className="text-xl font-semibold text-white mb-3">{agent.name}</h2>
                <p className="text-gray-400 text-sm line-clamp-3">
                  {agent.endpoint_info || 'No description available'}
                </p>
                <div className="mt-4 pt-4 border-t border-gray-600/50">
                  <span className="text-[#10a37f] text-sm font-medium">Start Chat →</span>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}



