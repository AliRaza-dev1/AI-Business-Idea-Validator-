import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth Services
export const auth = {
  register: (email, password) => api.post('/auth/register', { email, password }),
  login: (email, password) => api.post('/auth/login', { email, password }),
  getCurrentUser: () => api.get('/auth/me')
};

// Ideas Services
export const ideas = {
  create: (ideaData) => api.post('/ideas/', ideaData),
  getAll: (skip = 0, limit = 10) => api.get(`/ideas/?skip=${skip}&limit=${limit}`),
  getById: (ideaId) => api.get(`/ideas/${ideaId}`),
  update: (ideaId, ideaData) => api.put(`/ideas/${ideaId}`, ideaData),
  delete: (ideaId) => api.delete(`/ideas/${ideaId}`)
};

// Analysis Services
export const analysis = {
  triggerAnalysis: (ideaId) => api.post(`/analysis/${ideaId}/analyze`),
  getAnalysis: (ideaId) => api.get(`/analysis/${ideaId}`),
  getReport: (ideaId) => api.get(`/analysis/${ideaId}/report`)
};

export default api;
