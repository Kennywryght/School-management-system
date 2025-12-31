const API_URL = 'https://school-management-system-2-wck6.onrender.com/api';
//const API_URL = '/api';

// Helper function to handle responses
async function handleResponse(response) {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ 
      detail: `HTTP error! status: ${response.status}` 
    }));
    const err = new Error(error.detail || error.message || 'Request failed');
    err.response = {
      status: response.status,
      data: error
    };
    throw err;
  }
  return response.json();
}

// Helper function to get auth headers
function getAuthHeaders(token = null) {
  const headers = {
    'Content-Type': 'application/json',
  };
  
  const authToken = token || localStorage.getItem('token');
  if (authToken) {
    headers.Authorization = `Bearer ${authToken}`;
  }
  
  return headers;
}

// API object with common methods
const api = {
  get: async (endpoint, options = {}) => {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: 'GET',
      headers: getAuthHeaders(options.token),
      ...options
    });
    return { data: await handleResponse(response) };
  },
  
  post: async (endpoint, data, options = {}) => {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: 'POST',
      headers: getAuthHeaders(options.token),
      body: JSON.stringify(data),
      ...options
    });
    return { data: await handleResponse(response) };
  },
  
  put: async (endpoint, data, options = {}) => {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: 'PUT',
      headers: getAuthHeaders(options.token),
      body: JSON.stringify(data),
      ...options
    });
    return { data: await handleResponse(response) };
  },
  
  delete: async (endpoint, options = {}) => {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: 'DELETE',
      headers: getAuthHeaders(options.token),
      ...options
    });
    return { data: await handleResponse(response) };
  }
};

// Auth API calls
export const authAPI = {
  login: async (email, password) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData
    });
    
    return handleResponse(response);
  },
  
  getCurrentUser: async (token) => {
    const headers = {
      'Content-Type': 'application/json',
    };
    
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    } else {
      const storedToken = localStorage.getItem('token');
      if (storedToken) {
        headers.Authorization = `Bearer ${storedToken}`;
      }
    }
    
    const response = await fetch(`${API_URL}/auth/me`, {
      method: 'GET',
      headers
    });
    
    return handleResponse(response);
  },
};

export default api;