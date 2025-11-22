import axios from 'axios'
import { Agent, AgentCreate, AgentUpdate } from '@/types/agent'

// Get API URL from environment variable (.env.local)
// This must be set in .env.local file in the Frontend directory
const API_URL = process.env.NEXT_PUBLIC_API_URL

if (!API_URL) {
  throw new Error(
    'NEXT_PUBLIC_API_URL environment variable is required.\n' +
    'Please create a .env.local file in Admin-Portal/Frontend/ with:\n' +
    'NEXT_PUBLIC_API_URL=http://localhost:8000'
  )
}

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401 errors (unauthorized)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('admin_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const getAgents = async (): Promise<Agent[]> => {
  const response = await api.get<Agent[]>('/api/agents')
  return response.data
}

export const getAgent = async (agentId: string): Promise<Agent> => {
  const response = await api.get<Agent>(`/api/agents/${agentId}`)
  return response.data
}

export const createAgent = async (agent: AgentCreate): Promise<Agent> => {
  const response = await api.post<Agent>('/api/agents', agent)
  return response.data
}

export const updateAgent = async (agentId: string, agent: AgentUpdate): Promise<Agent> => {
  const response = await api.put<Agent>(`/api/agents/${agentId}`, agent)
  return response.data
}

export const deleteAgent = async (agentId: string): Promise<void> => {
  await api.delete(`/api/agents/${agentId}`)
}

// Authentication functions
export const login = async (password: string): Promise<{ success: boolean; token: string }> => {
  const response = await api.post<{ success: boolean; message: string; token: string }>('/api/auth/login', { password })
  return { success: response.data.success, token: response.data.token || '' }
}

export const verifyAuth = async (): Promise<boolean> => {
  try {
    await api.get('/api/auth/verify')
    return true
  } catch {
    return false
  }
}

