const API_BASE = (import.meta.env.VITE_API_URL as string | undefined) ?? 'http://localhost:5000'

export interface Run {
  id: number
  run_name: string
  scenario_name: string
  model_name: string
  provider: string
  agent_server: string | null
  start_datetime: string | null
  end_datetime: string | null
  total_time: number
  tokens_per_second: number | null
  follow_up_prompts: number
  input_tokens: number
  output_tokens: number
  total_tokens: number
  cost_usd: number | null
  output_text: string | null
  pass_fail: 'pass' | 'fail' | 'partial' | 'error' | null
  score: number | null
  error: boolean
  error_message: string | null
  grader_model: string | null
  grader_rationale: string | null
  suite_run_id: number | null
}

export interface RunsFilter {
  scenario?: string
  model?: string
  provider?: string
  from?: string
  to?: string
}

async function get<T>(path: string): Promise<T> {
  const resp = await fetch(`${API_BASE}${path}`)
  if (!resp.ok) throw new Error(`${resp.status} ${resp.statusText}`)
  return resp.json() as Promise<T>
}

export function fetchRuns(filter: RunsFilter = {}): Promise<Run[]> {
  const params = new URLSearchParams()
  if (filter.scenario) params.set('scenario', filter.scenario)
  if (filter.model) params.set('model', filter.model)
  if (filter.provider) params.set('provider', filter.provider)
  if (filter.from) params.set('from', filter.from)
  if (filter.to) params.set('to', filter.to)
  const qs = params.toString()
  return get<Run[]>(`/runs/${qs ? `?${qs}` : ''}`)
}

export function fetchRun(id: number): Promise<Run> {
  return get<Run>(`/runs/${id}`)
}
