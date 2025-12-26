import axios from 'axios';
const API_URL = 'https://school-management-system-2-wck6.onrender.com/api';
//const API_URL = '/api';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if it exists
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API calls
export const authAPI = {
  login: async (email, password) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await axios.post(`${API_URL}/auth/login`, formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },
  
  getCurrentUser: async (token) => {
    // Pass token directly if provided
    const headers = {};
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
    
    const response = await api.get('/auth/me', { headers });
    return response.data;
  },
};

export default api;