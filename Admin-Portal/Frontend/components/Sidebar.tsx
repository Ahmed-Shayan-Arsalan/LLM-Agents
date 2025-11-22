'use client'

import { Agent } from '@/types/agent'
import { useState } from 'react'
import { useRouter } from 'next/navigation'

interface SidebarProps {
  agents: Agent[]
  loading: boolean
  selectedAgent: Agent | null
  onSelectAgent: (agent: Agent) => void
  onAddNew: () => void
  onDelete: (agentId: string) => void
}

export default function Sidebar({
  agents,
  loading,
  selectedAgent,
  onSelectAgent,
  onAddNew,
  onDelete,
}: SidebarProps) {
  const [hoveredAgent, setHoveredAgent] = useState<string | null>(null)
  const router = useRouter()

  const handleLogout = () => {
    localStorage.removeItem('admin_token')
    router.push('/login')
  }

  return (
    <div className="w-64 bg-[#202123] flex flex-col border-r border-gray-700">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <button
          onClick={onAddNew}
          className="w-full flex items-center gap-3 px-4 py-3 bg-[#10a37f] hover:bg-[#0d8f6e] text-white rounded-lg font-medium transition-colors shadow-lg"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v16m8-8H4"
            />
          </svg>
          <span>New Bot</span>
        </button>
      </div>

      {/* Agents List */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#10a37f]"></div>
          </div>
        ) : agents.length === 0 ? (
          <div className="p-4 text-center text-gray-400 text-sm">
            <p>No agents yet</p>
            <p className="mt-2">Click "New Bot" to create one</p>
          </div>
        ) : (
          <div className="p-2">
            {agents.map((agent) => {
              const isSelected = selectedAgent?._id === agent._id
              const isHovered = hoveredAgent === agent._id

              return (
                <div
                  key={agent._id}
                  className={`group relative mb-1 rounded-lg transition-colors ${
                    isSelected
                      ? 'bg-[#343541] text-white'
                      : 'hover:bg-[#2f2f2f] text-gray-300'
                  }`}
                  onMouseEnter={() => setHoveredAgent(agent._id || null)}
                  onMouseLeave={() => setHoveredAgent(null)}
                >
                  <button
                    onClick={() => onSelectAgent(agent)}
                    className="w-full flex items-center gap-3 px-3 py-2.5 text-left"
                  >
                    <div className="flex-shrink-0 w-5 h-5 flex items-center justify-center">
                      <div className="w-2 h-2 rounded-full bg-[#10a37f]"></div>
                    </div>
                    <span className="flex-1 truncate text-sm font-medium">
                      {agent.name}
                    </span>
                  </button>

                  {/* Delete button on hover */}
                  {isHovered && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        if (agent._id) {
                          onDelete(agent._id)
                        }
                      }}
                      className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 text-gray-400 hover:text-red-400 rounded transition-colors"
                      title="Delete agent"
                    >
                      <svg
                        className="w-4 h-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                        />
                      </svg>
                    </button>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-700 space-y-3">
        <div className="text-xs text-gray-400 text-center">
          {agents.length} {agents.length === 1 ? 'agent' : 'agents'}
        </div>
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-2 px-3 py-2 text-gray-400 hover:text-white hover:bg-[#343541] rounded-lg transition-colors text-sm"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          <span>Logout</span>
        </button>
      </div>
    </div>
  )
}



