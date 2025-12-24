import api from './api.js';

// Student endpoints
export const studentAPI = {
  // Get my profile
  getProfile: async () => {
    const response = await api.get('/student/profile');
    return response.data;
  },
  
  // Get my results
  getMyResults: async (termId = null) => {
    const url = termId ? `/student/results?term_id=${termId}` : '/student/results';
    const response = await api.get(url);
    return response.data;
  },
  
  // Get results summary with position
  getResultsSummary: async (termId = null) => {
    const url = termId ? `/student/results/summary?term_id=${termId}` : '/student/results/summary';
    const response = await api.get(url);
    return response.data;
  },
};