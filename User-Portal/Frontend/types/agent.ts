export interface Agent {
  _id?: string
  name: string
  endpoint_info: string
}

export interface QueryRequest {
  agent_name: string
  user_query: string
}

export interface QueryResponse {
  generated_query: Record<string, any>
  success: boolean
  message?: string
}

export interface OpenAIRequest {
  agent_name: string
  user_query: string
  api_results: Record<string, any>
}

export interface OpenAIResponse {
  response: string
  success: boolean
  message?: string
}

export interface CompleteQueryResponse {
  response: string
  generated_query: Record<string, any>
  api_results: Record<string, any>
  success: boolean
}



