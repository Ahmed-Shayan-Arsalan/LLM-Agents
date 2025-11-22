'use client'

import { useState, useEffect } from 'react'
import { Agent, AgentCreate } from '@/types/agent'
import { createAgent, updateAgent } from '@/services/api'
import toast from 'react-hot-toast'

interface AgentDetailsProps {
  agent: Agent | null
  isCreating: boolean
  onClose: () => void
  onSuccess: () => void
}

export default function AgentDetails({
  agent,
  isCreating,
  onClose,
  onSuccess,
}: AgentDetailsProps) {
  const [isEditing, setIsEditing] = useState(isCreating)
  const [formData, setFormData] = useState<AgentCreate>({
    name: '',
    api_key: '',
    system_prompt: '',
    endpoint: '',
    endpoint_info: '',
    example_query: {},
    test_scenarios: '',
  })
  const [loading, setLoading] = useState(false)
  const [exampleQueryText, setExampleQueryText] = useState('')

  useEffect(() => {
    if (isCreating) {
      setIsEditing(true)
      setFormData({
        name: '',
        api_key: '',
        system_prompt: '',
        endpoint: '',
        endpoint_info: '',
        example_query: {},
        test_scenarios: '',
      })
      setExampleQueryText('')
    } else if (agent) {
      setFormData({
        name: agent.name,
        api_key: agent.api_key,
        system_prompt: agent.system_prompt,
        endpoint: agent.endpoint,
        endpoint_info: agent.endpoint_info,
        example_query: agent.example_query,
        test_scenarios: agent.test_scenarios,
      })
      setExampleQueryText(JSON.stringify(agent.example_query, null, 2))
      setIsEditing(false)
    }
  }, [agent, isCreating])

  const handleEditClick = () => {
    setIsEditing(true)
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleExampleQueryChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setExampleQueryText(e.target.value)
    try {
      const parsed = JSON.parse(e.target.value)
      setFormData((prev) => ({ ...prev, example_query: parsed }))
    } catch (error) {
      // Invalid JSON, will be caught on submit
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      let parsedQuery = formData.example_query
      if (exampleQueryText) {
        try {
          parsedQuery = JSON.parse(exampleQueryText)
        } catch (error) {
          toast.error('Invalid JSON in Example Query field')
          setLoading(false)
          return
        }
      }

      const submitData = {
        ...formData,
        example_query: parsedQuery,
      }

      if (agent?._id && !isCreating) {
        await updateAgent(agent._id, submitData)
        toast.success('Agent updated successfully')
      } else {
        await createAgent(submitData)
        toast.success('Agent created successfully')
      }

      setIsEditing(false)
      onSuccess()
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to save agent'
      toast.error(errorMessage)
      console.error('Error saving agent:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    if (isCreating) {
      onClose()
    } else {
      setIsEditing(false)
      // Reset form data to agent data
      if (agent) {
        setFormData({
          name: agent.name,
          api_key: agent.api_key,
          system_prompt: agent.system_prompt,
          endpoint: agent.endpoint,
          endpoint_info: agent.endpoint_info,
          example_query: agent.example_query,
          test_scenarios: agent.test_scenarios,
        })
        setExampleQueryText(JSON.stringify(agent.example_query, null, 2))
      }
    }
  }

  if (isEditing || isCreating) {
    return (
      <div className="flex-1 flex flex-col overflow-hidden bg-[#343541]">
        {/* Header */}
        <div className="px-8 py-5 border-b border-gray-700/50">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-semibold text-white">
              {isCreating ? 'Create New Agent' : `Edit ${agent?.name}`}
            </h1>
            <button
              onClick={handleCancel}
              className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-[#40414f] transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Form */}
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-4xl mx-auto px-8 py-6">
            <form onSubmit={handleSubmit} className="space-y-8">
              {/* Basic Information Section */}
              <div className="space-y-6">
                <h2 className="text-lg font-semibold text-gray-200 border-b border-gray-700/50 pb-2">
                  Basic Information
                </h2>
                
                <div className="grid grid-cols-1 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Name *
                    </label>
                    <input
                      type="text"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      required
                      className="w-full px-4 py-3 bg-[#40414f] border border-gray-600/50 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#10a37f] focus:border-transparent transition-all"
                      placeholder="Enter agent name"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      API Key *
                    </label>
                    <input
                      type="text"
                      name="api_key"
                      value={formData.api_key}
                      onChange={handleChange}
                      required
                      className="w-full px-4 py-3 bg-[#40414f] border border-gray-600/50 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#10a37f] focus:border-transparent transition-all font-mono text-sm"
                      placeholder="sk-..."
                    />
                  </div>
                </div>
              </div>

              {/* Configuration Section */}
              <div className="space-y-6">
                <h2 className="text-lg font-semibold text-gray-200 border-b border-gray-700/50 pb-2">
                  Configuration
                </h2>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    System Prompt *
                  </label>
                  <textarea
                    name="system_prompt"
                    value={formData.system_prompt}
                    onChange={handleChange}
                    required
                    rows={6}
                    className="w-full px-4 py-3 bg-[#40414f] border border-gray-600/50 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#10a37f] focus:border-transparent resize-none transition-all"
                    placeholder="Enter system prompt instructions..."
                  />
                </div>
              </div>

              {/* Endpoint Information Section - Large */}
              <div className="space-y-6">
                <h2 className="text-lg font-semibold text-gray-200 border-b border-gray-700/50 pb-2">
                  Endpoint Information
                </h2>
                
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      API Endpoint URL *
                    </label>
                    <input
                      type="url"
                      name="endpoint"
                      value={formData.endpoint}
                      onChange={handleChange}
                      required
                      className="w-full px-4 py-3 bg-[#40414f] border border-gray-600/50 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#10a37f] focus:border-transparent transition-all font-mono text-sm"
                      placeholder="https://api.example.com"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Endpoint Description & Context *
                    </label>
                    <textarea
                      name="endpoint_info"
                      value={formData.endpoint_info}
                      onChange={handleChange}
                      required
                      rows={8}
                      className="w-full px-4 py-3 bg-[#40414f] border border-gray-600/50 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#10a37f] focus:border-transparent resize-none transition-all"
                      placeholder="Provide a detailed description of the endpoint, including what it does, authentication requirements, rate limits, response format, use cases, and any other relevant contextual information..."
                    />
                    <p className="mt-2 text-xs text-gray-400">
                      Include details about authentication, rate limits, response format, use cases, and documentation links.
                    </p>
                  </div>
                </div>
              </div>

              {/* Query & Testing Section */}
              <div className="space-y-6">
                <h2 className="text-lg font-semibold text-gray-200 border-b border-gray-700/50 pb-2">
                  Query & Testing
                </h2>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Example Query (JSON) *
                  </label>
                  <textarea
                    name="example_query"
                    value={exampleQueryText}
                    onChange={handleExampleQueryChange}
                    required
                    rows={12}
                    className="w-full px-4 py-3 bg-[#40414f] border border-gray-600/50 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#10a37f] focus:border-transparent font-mono text-sm resize-none transition-all"
                    placeholder='{"type": "stemming", "query": {...}}'
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Test Scenarios *
                  </label>
                  <textarea
                    name="test_scenarios"
                    value={formData.test_scenarios}
                    onChange={handleChange}
                    required
                    rows={6}
                    className="w-full px-4 py-3 bg-[#40414f] border border-gray-600/50 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#10a37f] focus:border-transparent resize-none transition-all"
                    placeholder="Enter test scenarios..."
                  />
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3 pt-4 border-t border-gray-700/50">
                <button
                  type="button"
                  onClick={handleCancel}
                  className="px-6 py-2.5 border border-gray-600/50 rounded-lg text-gray-300 hover:bg-[#40414f] hover:border-gray-600 font-medium transition-all"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-6 py-2.5 bg-[#10a37f] hover:bg-[#0d8f6e] text-white rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-[#10a37f]/20"
                >
                  {loading ? 'Saving...' : isCreating ? 'Create Agent' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    )
  }

  // View mode
  if (!agent) return null

  return (
    <div className="flex-1 flex flex-col overflow-hidden bg-[#343541]">
      {/* Header */}
      <div className="px-8 py-5 border-b border-gray-700/50">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-white mb-1">{agent.name}</h1>
            {agent.created_at && (
              <p className="text-sm text-gray-400">
                Created {new Date(agent.created_at).toLocaleDateString('en-GB', { 
                  day: '2-digit', 
                  month: '2-digit', 
                  year: 'numeric' 
                })}
              </p>
            )}
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleEditClick}
              className="px-4 py-2 bg-[#40414f] hover:bg-[#4a4b5a] text-white rounded-lg font-medium transition-all flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              Edit
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-8 py-6">
          <div className="space-y-8">
            {/* Basic Information */}
            <div className="space-y-6">
              <h2 className="text-lg font-semibold text-gray-200 border-b border-gray-700/50 pb-2">
                Basic Information
              </h2>
              
              <div className="grid grid-cols-1 gap-6">
                <div>
                  <label className="block text-xs font-semibold text-gray-400 mb-2 uppercase tracking-wider">
                    API Key
                  </label>
                  <div className="px-4 py-3 bg-[#40414f] border border-gray-600/50 rounded-lg">
                    <code className="text-gray-300 text-sm font-mono">
                      {agent.api_key.substring(0, 20)}...
                    </code>
                  </div>
                </div>
              </div>
            </div>

            {/* Configuration */}
            <div className="space-y-6">
              <h2 className="text-lg font-semibold text-gray-200 border-b border-gray-700/50 pb-2">
                Configuration
              </h2>
              
              <div>
                <label className="block text-xs font-semibold text-gray-400 mb-2 uppercase tracking-wider">
                  System Prompt
                </label>
                <div className="px-4 py-3 bg-[#40414f] border border-gray-600/50 rounded-lg min-h-[120px]">
                  <p className="text-gray-300 whitespace-pre-wrap leading-relaxed">{agent.system_prompt}</p>
                </div>
              </div>
            </div>

            {/* Endpoint Information - Large Section */}
            <div className="space-y-6">
              <h2 className="text-lg font-semibold text-gray-200 border-b border-gray-700/50 pb-2">
                Endpoint Information
              </h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-gray-400 mb-2 uppercase tracking-wider">
                    API Endpoint URL
                  </label>
                  <div className="px-4 py-3 bg-[#40414f] border border-gray-600/50 rounded-lg">
                    <code className="text-blue-400 text-sm font-mono break-all">{agent.endpoint}</code>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-400 mb-3 uppercase tracking-wider">
                    Endpoint Description & Context
                  </label>
                  <div className="px-6 py-6 bg-[#40414f] border border-gray-600/50 rounded-lg min-h-[200px]">
                    <p className="text-gray-200 text-base leading-relaxed whitespace-pre-wrap">
                      {agent.endpoint_info}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Query & Testing */}
            <div className="space-y-6">
              <h2 className="text-lg font-semibold text-gray-200 border-b border-gray-700/50 pb-2">
                Query & Testing
              </h2>
              
              <div>
                <label className="block text-xs font-semibold text-gray-400 mb-2 uppercase tracking-wider">
                  Example Query
                </label>
                <div className="px-4 py-3 bg-[#40414f] border border-gray-600/50 rounded-lg">
                  <pre className="text-gray-300 text-sm font-mono overflow-x-auto">
                    {JSON.stringify(agent.example_query, null, 2)}
                  </pre>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-400 mb-2 uppercase tracking-wider">
                  Test Scenarios
                </label>
                <div className="px-4 py-3 bg-[#40414f] border border-gray-600/50 rounded-lg min-h-[100px]">
                  <p className="text-gray-300 whitespace-pre-wrap leading-relaxed">{agent.test_scenarios}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
