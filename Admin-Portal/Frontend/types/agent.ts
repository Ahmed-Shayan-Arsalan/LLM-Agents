export interface Agent {
  _id?: string
  name: string
  api_key: string
  system_prompt: string
  endpoint: string
  endpoint_info: string
  example_query: Record<string, any>
  test_scenarios: string
  created_at?: string
}

export interface AgentCreate {
  name: string
  api_key: string
  system_prompt: string
  endpoint: string
  endpoint_info: string
  example_query: Record<string, any>
  test_scenarios: string
}

export interface AgentUpdate {
  name?: string
  api_key?: string
  system_prompt?: string
  endpoint?: string
  endpoint_info?: string
  example_query?: Record<string, any>
  test_scenarios?: string
}



