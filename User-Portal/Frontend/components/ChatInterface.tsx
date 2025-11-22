'use client'

import { useState, useRef, useEffect } from 'react'
import { Agent } from '@/types/agent'
import { completeQuery } from '@/services/api'
import toast from 'react-hot-toast'

interface ChatInterfaceProps {
  agent: Agent
  agents: Agent[]
  onBack: () => void
  onSwitchAgent: (agent: Agent) => void
}

interface Message {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
}

export default function ChatInterface({ agent, agents, onBack, onSwitchAgent }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [showAgentDropdown, setShowAgentDropdown] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const previousAgentIdRef = useRef<string | null>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Add system message when agent changes (but not on initial load)
  useEffect(() => {
    const currentAgentId = agent._id || null
    
    // Skip on initial load
    if (previousAgentIdRef.current === null) {
      previousAgentIdRef.current = currentAgentId
      return
    }
    
    // Only add system message if agent actually changed and we have messages
    if (previousAgentIdRef.current !== currentAgentId && messages.length > 0) {
      const systemMessage: Message = {
        role: 'system',
        content: `Switched to ${agent.name}`,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, systemMessage])
    }
    
    // Update the ref
    previousAgentIdRef.current = currentAgentId
  }, [agent._id, agent.name, messages.length])

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement
      if (showAgentDropdown && !target.closest('.agent-dropdown-container')) {
        setShowAgentDropdown(false)
      }
    }

    if (showAgentDropdown) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [showAgentDropdown])

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    const userQuery = input.trim()
    setInput('')
    setLoading(true)

    try {
      const response = await completeQuery({
        agent_name: agent.name,
        user_query: userQuery,
      })

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to get response')
      console.error('Error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex h-screen flex-col bg-[#343541] text-gray-100 animate-fadeIn">
      {/* Header */}
      <div className="px-8 py-5 border-b border-gray-700/50">
        <div className="flex items-center justify-between max-w-4xl mx-auto">
          <div className="flex items-center gap-4">
            <button
              onClick={onBack}
              className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-[#40414f] transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <div className="relative agent-dropdown-container">
              <button
                onClick={() => setShowAgentDropdown(!showAgentDropdown)}
                className="flex items-center gap-2 px-4 py-2 bg-[#40414f] hover:bg-[#4a4b5a] rounded-lg transition-colors"
              >
                <span className="text-xl font-semibold text-white">{agent.name}</span>
                <svg className={`w-4 h-4 text-gray-400 transition-transform ${showAgentDropdown ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              
              {showAgentDropdown && (
                <div className="absolute top-full left-0 mt-2 bg-[#40414f] border border-gray-600 rounded-lg shadow-lg z-50 min-w-[250px] animate-slideDown">
                  {agents.map((a) => (
                    <button
                      key={a._id}
                      onClick={() => {
                        if (a._id === agent._id) {
                          // Same agent, just close dropdown
                          setShowAgentDropdown(false)
                          return
                        }
                        // Switch agent (conversation history is preserved)
                        toast.success(`Switched to ${a.name}`, {
                          icon: '🤖',
                          style: {
                            background: '#10a37f',
                            color: '#fff',
                          },
                        })
                        onSwitchAgent(a)
                        setShowAgentDropdown(false)
                      }}
                      className={`w-full text-left px-4 py-3 hover:bg-[#4a4b5a] transition-colors first:rounded-t-lg last:rounded-b-lg flex items-center justify-between ${
                        a._id === agent._id ? 'bg-[#10a37f]/20 text-[#10a37f] font-semibold' : 'text-white'
                      }`}
                    >
                      <span>{a.name}</span>
                      {a._id === agent._id && (
                        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>
            <p className="text-sm text-gray-400">AI Assistant</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-8 py-6">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full animate-fadeIn">
              <div className="text-center">
                <div className="text-6xl mb-4 animate-bounce">🤖</div>
                <h2 className="text-2xl font-semibold text-gray-300 mb-2">
                  Start a conversation with {agent.name}
                </h2>
                <p className="text-gray-400">
                  Ask a question to get started
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {messages.map((message, index) => {
                // System message (bot switch indicator)
                if (message.role === 'system') {
                  return (
                    <div key={index} className="flex items-center justify-center my-4 animate-fadeIn">
                      <div className="flex items-center gap-3 px-4 py-2 bg-[#40414f]/50 border border-[#10a37f]/30 rounded-full">
                        <div className="w-2 h-2 bg-[#10a37f] rounded-full animate-pulse"></div>
                        <span className="text-sm text-gray-400 italic">
                          {message.content} • {message.timestamp.toLocaleTimeString()}
                        </span>
                        <div className="w-2 h-2 bg-[#10a37f] rounded-full animate-pulse"></div>
                      </div>
                    </div>
                  )
                }
                
                // User or Assistant message
                return (
                  <div
                    key={index}
                    className={`flex gap-4 animate-slideIn ${
                      message.role === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    {message.role === 'assistant' && (
                      <div className="w-8 h-8 bg-[#10a37f] rounded-full flex items-center justify-center flex-shrink-0">
                        🤖
                      </div>
                    )}
                    <div
                      className={`max-w-[80%] rounded-lg px-4 py-3 ${
                        message.role === 'user'
                          ? 'bg-[#10a37f] text-white'
                          : 'bg-[#40414f] text-gray-200'
                      }`}
                    >
                      <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
                    </div>
                    {message.role === 'user' && (
                      <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center flex-shrink-0">
                        👤
                      </div>
                    )}
                  </div>
                )
              })}
              {loading && (
                <div className="flex gap-4 justify-start animate-fadeIn">
                  <div className="w-8 h-8 bg-[#10a37f] rounded-full flex items-center justify-center flex-shrink-0">
                    🤖
                  </div>
                  <div className="bg-[#40414f] rounded-lg px-4 py-3">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </div>

      {/* Input */}
      <div className="border-t border-gray-700/50 px-8 py-4">
        <form onSubmit={handleSend} className="max-w-4xl mx-auto">
          <div className="flex gap-4">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              disabled={loading}
              className="flex-1 px-4 py-3 bg-[#40414f] border border-gray-600/50 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#10a37f] focus:border-transparent disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="px-6 py-3 bg-[#10a37f] hover:bg-[#0d8f6e] text-white rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              Send
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}



