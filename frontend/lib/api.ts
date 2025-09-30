import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Query API
export const queryAPI = {
  sendQuery: async (query: string, context?: any) => {
    const response = await api.post('/api/v1/query', {
      query,
      context,
    })
    return response.data
  },
}

// Files API
export const filesAPI = {
  listFiles: async () => {
    const response = await api.get('/api/v1/files')
    return response.data
  },
  
  listDatasets: async () => {
    const response = await api.get('/api/v1/datasets')
    return response.data
  },
}

// Ingestion API
export const ingestionAPI = {
  ingestDrive: async () => {
    const response = await api.post('/api/v1/ingest/drive')
    return response.data
  },
  
  ingestBox: async () => {
    const response = await api.post('/api/v1/ingest/box')
    return response.data
  },
}

// Health API
export const healthAPI = {
  checkHealth: async () => {
    const response = await api.get('/api/v1/health')
    return response.data
  },
}

export default api
