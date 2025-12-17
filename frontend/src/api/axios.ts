const API_BASE_URL = 'http://localhost:8000';

const buildUrl = (url: string, params?: Record<string, any>) => {
  const target = new URL(`${API_BASE_URL}${url}`, window.location.origin)

  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null) {
        target.searchParams.append(k, String(v))
      }
    })
  }

  return target.toString()
}

async function request<T>(
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE',
  url: string,
  params?: Record<string, any>
) {
  const finalUrl = buildUrl(url, params)

  const res = await fetch(finalUrl, { method, credentials: 'include' })

  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `Request failed: ${res.status}`)
  }

  return res.json() as T
}

const apiClient = {
  get: <T>(url: string, params?: any) => request<T>('GET', url, params),
}

export default apiClient
