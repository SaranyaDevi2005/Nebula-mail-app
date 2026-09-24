import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({ baseURL: API_URL })

export const getInbox = () => api.get('/api/inbox').then(r => r.data)
export const getSent = () => api.get('/api/sent').then(r => r.data)
export const getMessage = (id) => api.get(`/api/messages/${id}`).then(r => r.data)
export const sendEmail = (payload) => api.post('/api/send', payload).then(r => r.data)
export const searchEmails = (params) => api.get('/api/search', { params }).then(r => r.data)
export const askAssistant = (message, context) =>
  api.post('/api/assistant', { message, context }).then(r => r.data)
export const authStatus = () => api.get('/auth/status').then(r => r.data)
export const loginUrl = () => `${API_URL}/auth/login`
