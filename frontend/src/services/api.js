const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

async function post(path, payload) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    const detail = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail || data)
    throw new Error(detail || `HTTP ${response.status}`)
  }
  return data
}

export const runSimulation = (payload) => post('/api/simulation/run', payload)
export const runOptimization = (payload) => post('/api/optimization/run', payload)
