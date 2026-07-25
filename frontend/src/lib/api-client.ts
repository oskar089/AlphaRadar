import type { ApiError } from './types'

class ApiClientError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiClientError'
    this.status = status
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (response.ok) {
    if (response.status === 204) return undefined as T
    return response.json() as Promise<T>
  }

  let detail: string
  try {
    const body: ApiError = await response.json()
    detail = body.detail
  } catch {
    detail = response.statusText
  }

  switch (response.status) {
    case 404:
      throw new ApiClientError(404, detail || 'Resource not found')
    case 422:
      throw new ApiClientError(422, detail || 'Validation error')
    case 503:
      throw new ApiClientError(503, detail || 'Service unavailable')
    default:
      throw new ApiClientError(
        response.status,
        response.status >= 500
          ? 'Internal server error'
          : detail || `Request failed (${response.status})`,
      )
  }
}

export const apiClient = {
  async get<T>(path: string): Promise<T> {
    const response = await fetch(path)
    return handleResponse<T>(response)
  },

  async post<T>(path: string, body: unknown): Promise<T> {
    const response = await fetch(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    return handleResponse<T>(response)
  },

  async delete(path: string): Promise<void> {
    const response = await fetch(path, { method: 'DELETE' })
    await handleResponse<unknown>(response)
  },
}

export { ApiClientError }
