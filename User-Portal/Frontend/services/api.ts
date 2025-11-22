import axios from 'axios'
import { Agent, QueryRequest, QueryResponse, OpenAIRequest, OpenAIResponse, CompleteQueryResponse } from '@/types/agent'

const API_URL = process.env.NEXT_PUBLIC_API_URL

if (!API_URL) {
  throw new Error(
    'NEXT_PUBLIC_API_URL environment variable is required.\n' +
    'Please create a .env.local file in User-Portal/Frontend/ with:\n' +
    'NEXT_PUBLIC_API_URL=http://localhost:8000'
  )
}

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const getAgents = async (): Promise<Agent[]> => {
  const response = await api.get<Agent[]>('/api/agents')
  return response.data
}

export const getAgent = async (agentName: string): Promise<Agent> => {
  const response = await api.get<Agent>(`/api/agents/${agentName}`)
  return response.data
}

export const generateQuery = async (request: QueryRequest): Promise<QueryResponse> => {
  const response = await api.post<QueryResponse>('/api/generate-query', request)
  return response.data
}

export const getOpenAIResponse = async (request: OpenAIRequest): Promise<OpenAIResponse> => {
  const response = await api.post<OpenAIResponse>('/api/get-response', request)
  return response.data
}

export const completeQuery = async (request: QueryRequest): Promise<CompleteQueryResponse> => {
  const response = await api.post<CompleteQueryResponse>('/api/complete-query', request)
  return response.data
}

