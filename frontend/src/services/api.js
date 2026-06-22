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
  register: (email, password, full_name, role="user") => api.post('/auth/register', { email, password, full_name, role }),
  login: (email, password) => api.post('/auth/login', { email, password }),
  getCurrentUser: () => api.get('/auth/me')
};

// Ideas Services
export const ideas = {
  create: (ideaData) => api.post('/ideas/', ideaData),
  getAll: (skip = 0, limit = 10, search = '', status = '') => {
    let url = `/ideas/?skip=${skip}&limit=${limit}`;
    if (search) url += `&search=${search}`;
    if (status) url += `&status=${status}`;
    return api.get(url);
  },
  getById: (ideaId) => api.get(`/ideas/${ideaId}`),
  update: (ideaId, ideaData) => api.put(`/ideas/${ideaId}`, ideaData),
  delete: (ideaId) => api.delete(`/ideas/${ideaId}`),
  getRecommendations: () => api.get('/ideas/user/recommendations')
};

// Analysis Services
export const analysis = {
  triggerAnalysis: (ideaId) => api.post(`/analysis/${ideaId}/analyze`),
  getAnalysis: (ideaId) => api.get(`/analysis/${ideaId}`),
  getReport: (ideaId) => api.get(`/analysis/${ideaId}/report`),
  compareAnalyses: (ideaA, ideaB) => api.get(`/analysis/compare?idea_a=${ideaA}&idea_b=${ideaB}`),
  getMonitoringStats: () => api.get('/analysis/monitoring/stats')
};

// Reports Services
export const reports = {
  getPdfReport: (ideaId) => api.get(`/ideas/${ideaId}/report/pdf`, { responseType: 'blob' }),
  getJsonReport: (ideaId) => api.get(`/ideas/${ideaId}/report/json`)
};

// Dashboard Services
export const dashboard = {
  getStats: () => api.get('/dashboard/stats'),
  getAdvancedStats: () => api.get('/dashboard/advanced-analytics')
};

export default api;
